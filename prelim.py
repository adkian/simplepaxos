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
(priests will track these for changes by messengers)

from,code,ballot,decree

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
4: failed ballot
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
- leader.evaluate
- messenger.send_message (condensed messenger)
TODO: 
- leader: randomize sets of priests for different ballots and wait only for a majority (and not everyone) to respond with lastVote
- actually satisfy B1 by changing the offset method to make sure that ballot numbers for different presidents are ascending in value 

TODO future: 
- multiple god instance support
- split classes into different files for readability
- implement priest promise after lastvote (one idea: priest send a message to himself. this would require a new field in messagebook: 'outgoing/self')

TODO far future: 
- change communications between priests to socket communications instead of file io
===============================
"""



"""
paxons are very religious; god controls anything and everything 

- literally creates priests ie initializes the objects 
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
                self.priests[name] = priest(name, (name+1)*offset, True, num_ballots)
            else:
                self.priests[name] = priest(name, (name+1)*offset, False, num_ballots)
                
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

    def send_message(self, to, code, ballot, decree):
        message = [[self.serving_priest, code, ballot, decree]]
        msg_df = pd.DataFrame(data=message)
        with open('messages/'+str(to), 'a') as f:
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
        
    def __init__(self, name, start_offset, is_leader, ballot_count): #is_leader: temporary var for single ballot test
        Thread.__init__(self)
        self.name = name 
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

        self.ballot_count = ballot_count
        self.ballots_done = 0

        self.decree=-1
        
    def run(self):
        if(self.is_leader):
            while self.ballots_done < self.ballot_count:
                print("LOG: *****Starting ballot #" + str(self.ballots_done+1) + " *******")
                self.leader_main()
                self.ballots_done += 1
        else:
            while self.ballots_done < self.ballot_count:
                self.priest_main()
                self.ballots_done += 1

    #=====================leader functions===================
    def leader_main(self):
        print("LOG: " + self.name + " is the leader")
        try:
            ledger_data = pd.read_csv(self.ledger)
            last_ballot_num = ledger_data.at[ledger_data.shape[0]-1,'ballot']
            #B1 is satisfied assuming num_ballots < difference between offsets (currently 100)
            ballot_num = self.offset + (int(last_ballot_num)%100) + 1
            self.decree = ledger_data.at[ledger_data.shape[0]-1,'decree']
        except pd.errors.EmptyDataError: #first ballot ever
            ballot_num = self.offset+1
            self.decree += 1
        except ValueError: #first ballot ever
            ballot_num = self.offset+1
            self.decree += 1
            
        print("LOG: Leader initiating ballot #" + str(ballot_num))
        self.next_ballot(ballot_num, self.decree)

        #block till majority set sends lastvote
        # temporary: block till all priests send responses
        responses = 0
        quorum = []        #responded priests
        voted_ballot = 0

        while responses < len(self.priests.keys())-1: 
            msg = self.new_message()
            quorum.append(int(msg[0]))
            responses += 1
            #note priest voted decree to satisfy b3
            if int(msg[2]) >= 0 and int(msg[2] > voted_ballot):
                voted_ballot = int(msg[2])
                self.decree = int(msg[3])
        print("LOG: leader got all lastVotes, beginning ballot")
        
        self.begin_ballot(quorum, self.decree, ballot_num)

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
            self.send_ballot_result(quorum, ballot_num, self.decree, 3)  
            #make entry in ledger
            ledger_entry = [[ballot_num, self.decree]]
            ledger_entry_df = pd.DataFrame(data = ledger_entry)
            with open(self.ledger, 'a') as f:
                ledger_entry_df.to_csv(f, header=False, index=False)
            self.decree+=1
        else:
            #send failed code
            print("LOG: ballot failed")
            self.send_ballot_result(quorum, ballot_num, self.decree, 4)
            
    def next_ballot(self, ballot, decree):
        priests = self.priests.keys()
        code = 1 #nextballot code
        for priest_name in priests:
            if str(priest_name) == str(self.name):
                continue
            else:
                self.messenger.send_message(priest_name, code, ballot, decree)

    """send message to every priest indicating that his vote is requested"""
    def begin_ballot(self, quorum, ballot, decree):
        code = 2 #beginBallot code
        for priest in quorum:            
            self.messenger.send_message(priest, code, ballot, decree)


    def send_ballot_result(self,quorum, ballot, decree, result):
        code = result # ballot result code
        for priest in quorum:
            self.messenger.send_message(priest, code, ballot, decree)

        
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
                if vote_yes < 80: #change this value to vary probability 
                    self.vote(leader, 2, msg[2], msg[3])
                else:
                    self.vote(leader, 3, msg[2], msg[3])

        msg = self.new_message() #block for success (or failure) message
        if msg[0] == leader and msg[1] == 3:
            print("LOG: priest #" + self.name + " writing sucessful ballot in ledger")
            ledger_entry = [[msg[2], msg[3]]]
            ledger_entry_df = pd.DataFrame(data = ledger_entry)
            with open(self.ledger, 'a') as f:
                ledger_entry_df.to_csv(f, header=False, index=False)
        elif msg[0] == leader and msg[1] == 4:
            pass

    """determine the lastVote and send it to the leader (if not promised to another leader)"""        
    def last_vote(self,leader):    
        ballot= -1 # lastVoted ballot
        code = 1 # lastVote code
        decree = -1 #lastVote decree
        
        try:
            ledger = pd.read_csv(self.ledger)
            for entry in reversed(range(ledger.shape[0],0)):
                if(entry['voted']==1):
                    ballot = entry['ballot_num']
                    decree = entry['decree']
                    break
        except pd.errors.EmptyDataError:
            pass

        #TODO: check for promises before responding, set promise to 1 after next message
        self.messenger.send_message(leader, code, ballot, decree)
        

    def vote(self, leader, vote, ballot, decree):
        self.messenger.send_message(leader, vote, ballot, decree)


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
