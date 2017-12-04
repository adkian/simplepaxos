import pandas as pd
import random
import time
from threading import Thread


"""
===============================

priest ledger format:
ballot number, decree
n,d

===============================

priest messagebook format: 
(priests will track these for changes by messenger)

from,code,voted_at_ballot=-1,decree=-1

n,1/2/3,(voted at) ballot_number, (voted for) decree

voted_at_ballot:                   responding to next_ballot from priests
decree                             decree voted at

codes (to leader): 
1: last vote
2: vote: yes
3: vote: no

codes (from leader):
1: next ballot
2: begin ballot
3: succesful ballot
===============================

sequence of function writing (follow this when evaluating):
- skeleton
- priest init
- leader_main
- god init
- leader.next_ballot
- messenger init
- leader.messenger.send_next_ballot
- priest_main
- priest.messenger.send_last_vote
- leader.begin_ballot
- leader.messenger.send_begin_ballot
- priest.vote
- priest.messenger.send_vote
TODO: 
- leader.evaluate

TODO future: 
- condense all messaging functions into a single one using codes
- split classes into different files for readability
- implement priest promise after lastvote (one idea: priest send a message to himself. this would require a new field in messagebook: 'outgoing/self')

TODO far future: 
- change communications between priests to socket communications instead of file io
===============================
"""



"""
paxons are very religious; god controls anything and everything 

- literally creates priests ie initializes the objects 
- assigns ballot number ranges for each priest (so B1 is satisfied)
"""    
class god:
    
    num_priests = 0
    priests = {} #key:value ~ priest name : priest instance
    messengers = []
    def __init__(self, num_priests, num_ballots, offset=100): 
        self.num_priests = num_priests
        self.num_ballots = num_ballots

        random_leader = random.randint(0,num_priests-1)
        #create and name the priests and messengers (quite godly)
        for name in range(0, self.num_priests):
            if name == random_leader:
                self.priests[name] = priest(name, (name+1)*offset, True)
            else:
                self.priests[name] = priest(name, (name+1)*offset, False)
                
        for priest_name in self.priests.keys():
            self.priests[priest_name].start()
        
        for priest_name in self.priests.keys():
            self.priests[priest_name].join()            


"""
messenger relays messages to and from the leader and the priest
she accomplishes this by tracking the priests' ledger files for changes

each priest (including the leader) has a personal messenger (instance)
"""

class messenger(god):

    def __init__(self, serving_priest):
        self.serving_priest = serving_priest
    
    """
    leader messenger functions
    """        
    def send_next_ballot(self,current_list, ballot_num):
        message = [[self.serving_priest,1,ballot_num,-1]]
        msg_df = pd.DataFrame(data = message)
        for priest_name in current_list:
            if str(priest_name) == str(self.serving_priest):
                pass
            else:
                print("LOG: leader sending message to priest #" + str(priest_name))
                with open('messages/'+str(priest_name), 'a') as f:
                    msg_df.to_csv(f, header=False, index=False)        
                
    def send_begin_ballot(self, quorum, decree, ballot_num):
        message = [[self.serving_priest,2,ballot_num,decree]]
        msg_df = pd.DataFrame(data = message)
        for priest_name in quorum:
            print("LOG: leader sending beginBallot to priest #" + str(priest_name))
            with open('messages/'+str(priest_name), 'a') as f:
                msg_df.to_csv(f, header=False, index=False)        

    
    def send_on_success(self):
        pass
        
    """
    priest messenger functions
    """
    def send_last_vote(self,ballot_num, leader_num):
        #TODO logic for sending voted at decree in the message (-1 for now)
        message = [[self.serving_priest,1,ballot_num,-1]]
        msg_df = pd.DataFrame(data = message)
        with open('messages/'+str(leader_num), 'a') as f:
            print("LOG: priest #" + self.serving_priest + " sending lastVote to leader priest #" + str(leader_num))
            msg_df.to_csv(f, header=False, index=False)        

    def send_vote(self, leader, vote, ballot_num, decree):
        message = [[self.serving_priest,vote,ballot_num,decree]]
        msg_df = pd.DataFrame(data = message)
        with open('messages/'+str(leader), 'a') as f:
            print("LOG: priest #" + self.serving_priest + " sending Vote to leader priest")
            msg_df.to_csv(f, header=False, index=False)                
        
        
"""
priests are present (or not present) and vote (or not vote) for ballots proposed 
by the leader 
they record all ballots they have participated in in individual ledger files

start offset is the offset by which a priest starts assigning ballot numbers when 
he is assigned leader to satisfy B1

ex. priests (A, B, C) have offsets (100, 200, 300) (this assumes maximum of 99 ballots)
leader sequence (determined randomly by god): A B A C B A
resulting ballot numbers: 100 200 101 300 201 102
"""    
class priest(messenger, Thread):
        
    def __init__(self, name, start_offset, is_leader): #is_leader: temporary var for single ballot test
        Thread.__init__(self)
        self.name = name #write this name in the ledger in case it gets lost (ledger fileaname)
        self.messenger = messenger(self.name) #hire a messenger
        self.ledger = "ledgers/" + self.name
        self.messagebook = "messages/" + self.name


        
        with open(self.ledger, 'w') as ledgerfile:
            ledgerfile.write("ballot,decree\n")
        
        with open(self.messagebook, 'w') as msgbookfile:
             msgbookfile.write("from,code,ballot,decree\n")
        self.messages_recieved = 0
        
        self.offset = start_offset                    
        self.is_leader = is_leader

    def run(self):
        if(self.is_leader):
            self.leader_main()
        else:
            self.priest_main()
    #=====================leader functions===================
    def leader_main(self):
        print("LOG: " + self.name + " is the leader")
        try:
            ledger_data = pd.read_csv(self.ledger)
            last_ballot_num= ledger_data.at[ledger_data.shape[0]-1,'ballot_num']
            #B1 is satisfied assuming num_ballots < difference between offsets (currently 100)
            ballot_num = self.offset + (int(last_ballot_num)%100) + 1 
        except pd.errors.EmptyDataError: #first pallot ever
            ballot_num = self.offset+1
        except ValueError: #first ballot ever
            ballot_num = self.offset+1
            

        print("LOG: Leader initiating ballot #" + str(ballot_num))
        self.next_ballot(ballot_num)

        #block till majority set sends lastvote
        # temporary: block till all priests send responses
        responses = 0
        quorum = []        #responded priests
        voted_ballot = 0
        voted_decree = -1
        while responses < len(self.priests.keys())-1: 
            msg = self.new_message()
            quorum.append(int(msg[0]))
            responses += 1
            #note priest voted decree to satisfy b3
            if int(msg[2]) >= 0 and int(msg[2] > voted_ballot):
                voted_ballot = int(msg[2])
                voted_decree = int(msg[3])
        print("LOG: leader got all lastVotes, beginning ballot")

        if voted_decree < 0:
            voted_decree += 1
        
        self.begin_ballot(quorum, voted_decree, ballot_num)

        #block till all votes recieved
        votes = 0
        votes_yes = 0
        while votes < len(quorum):
            msg = self.new_message()
            votes += 1
            if msg[1] == 2:
                votes_yes += 1
                
        if votes_yes == len(quorum):
            print("LOG: ballot was successful, writing in ledger")
            self.send_successful(quorum)            
            #make entry in ledger
            ledger_entry = [[ballot_num, voted_decree]]
            ledger_entry_df = pd.DataFrame(data = ledger_entry)
            with open(self.ledger, 'a') as f:
                ledger_entry_df.to_csv(f, header=False, index=False)
        
    def next_ballot(self,ballot_num):
        #randomly choose a number of priests: 40% - 100% of total priests
        #rand_num = random.randrange(self.num_priests*0.4, self.num_priests+1)

        #current_priests = random.sample(self.priests.keys(), rand_num)        
        current_priests = self.priests.keys()
        
        #Send the nextBallot message to the priests and wait for their responses
        self.messenger.send_next_ballot(current_priests, ballot_num)
        #wait for priests' responses

    def begin_ballot(self, quorum, decree, ballot_num):
        self.messenger.send_begin_ballot(quorum, decree, ballot_num)
        #send message to every priest indicating that his vote is requested

    def send_successful(self,quorum):
        pass
        #check if the ballot was a success and note the decree if it was

        #send the sucess message to all living priests

        
    #====================regular priest functions======================
    
    def priest_main(self):
        print("LOG: " + self.name + " is a priest")
        msg = self.new_message() #block for nextBallot from leader
        leader = msg[0] # leader 
        print("LOG: priest #" + self.name + " recieved msg from #" + str(leader))
        self.last_vote(leader)

        while msg[1] != 2:            
            msg = self.new_message() # block for beginBallot from leader
            if(msg[1] == 2): # recieved beginBallot
                #TODO probability of voting variable
                #currently: 100% probability of voting yes
                vote_yes = random.randrange(0,99)
                if vote_yes < 100: #change this value to vary probability 
                    self.vote(leader, 2, msg[2], msg[3])
                else:
                    vote(leader, 3, msg[2], msg[3])
                    
    def last_vote(self,leader_num):    
        #determine the lastVote and send it to the leader (if not promised to another leader) (might
        #need another function for this)
        ledger = pd.read_csv(self.ledger)
        last_voted = -1        
        for entry in reversed(range(ledger.shape[0],0)):
            if(entry['voted']==1):
                last_voted = entry['ballot_num']
                break
        
        #responding to a next_ballot request from the leader
        #TODO: check for promises before responding
        self.messenger.send_last_vote(last_voted, int(leader_num))
        #TODO: if responded, set promise to 1 for the relevant maxVote in the ledger        
        

    def vote(self, leader, vote, ballot_num, decree):
        self.messenger.send_vote(leader, vote, ballot_num, decree)

    def on_success():
        pass
        #do something if the messenger brings the good news of a ballot success

    #======================general functions============================
        
    def new_message(self):
        #block till new message read, return message when read
                
        while True:
            time.sleep(0.4)
            try:
                msgbook_data = pd.read_csv(self.messagebook)              
                if(msgbook_data.shape[0]>self.messages_recieved):
                    message=msgbook_data.iloc[[self.messages_recieved]].values.tolist()[0]
                    self.messages_recieved += 1
                    print("LOG: leader recieved msg from priest #" + str(message[0]))
                    return message
            
            except pd.errors.EmptyDataError:
                pass

    

if __name__ == '__main__':
    god_instance = god(3,5)
