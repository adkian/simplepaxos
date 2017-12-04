import pandas as pd
import random
import time
from threading import Thread


"""
===============================

priest ledger format:
ballot number, voted or not, promised or not, times led
n,0/1,0/1,x  

promised or not explanation:       whether or not this priest has promised to not 
                                   respond to maxvote requests after this ballot
times led explanation:             number of times she's been leader
                                   (see doc for messenger)
===============================

priest messagebook format: 
(priests will track these for changes by messenger)

from,code,voted_at_ballot=-1
n,1/2/3,ballot_number

voted_at_ballot:                   responding to next_ballot from priests

codes (to leader): 
1: last vote
2: begin ballot
3: successful ballot

codes (from leader):
1: next ballot
2: begin ballot
3: succesful ballot
===============================

sequence of function writing:
- skeleton
- priest init
- leader_main
- god init
- next_ballot
- messenger init
- send_next_ballot
- priest_main

TODO next: 
- send_last_vote

TODO future: 
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
        message = [[self.serving_priest,1]]
        msg_df = pd.DataFrame(data = message)
        for priest_name in current_list:
            if str(priest_name) == str(self.serving_priest):
                pass
            else:
                print("LOG: leader sending message to priest #" + str(priest_name))
                with open('messages/'+str(priest_name), 'a') as f:
                    msg_df.to_csv(f, header=False, index=False)        
                
    def send_begin_ballot(self):
        pass
    
    def send_on_success(self):
        pass
        
    """
    priest messenger functions
    """
    def send_last_vote(self,ballot_num, leader_num):
        message = [[self.serving_priest,1,ballot_num]]
        msg_df = pd.DataFrame(data = message)
        with open('messages/'+str(leader_num), 'a') as f:
            print("LOG: priest #" + self.serving_priest + " sending lastVote to leader")
            msg_df.to_csv(f, header=False, index=False)        

    def send_vote():
        pass
        
        
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

        self.messages_recieved = 0
        
        # with open(self.ledger, 'w') as ledgerfile:
        #     ledgerfile.write("ballot_num,voted,promised,times_led")
        
        with open(self.messagebook, 'w') as msgbookfile:
             msgbookfile.write("from,code,ballot\n")
        
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
            times_led = ledger_data.at[ledger_data.shape[0]-1,'times_led'] #last col of last row of ledger
        except pd.errors.EmptyDataError:
            times_led = 0
            
        ballot_num = self.offset + int(times_led) #B1 is satisfied assuming num_ballots < difference between offsets
        print("LOG: Leader initiating ballot #" + str(ballot_num))
        self.next_ballot(ballot_num)
        self.begin_ballot()
        
    def next_ballot(self,ballot_num):
        #randomly choose a number of priests: 40% - 100% of total priests
        #rand_num = random.randrange(self.num_priests*0.4, self.num_priests+1)

        #current_priests = random.sample(self.priests.keys(), rand_num)        
        current_priests = self.priests.keys()
        
        #Send the nextBallot message to the priests and wait for their responses
        self.messenger.send_next_ballot(current_priests, ballot_num)
        #next ballot vote will begin

    def begin_ballot(self):
        pass
        #wait for all threads to respond
        #send message to every priest indicating that his vote is requested

    def evaluate():
        pass
        #check if the ballot was a success and note the decree if it was

        #send the sucess message to all living priests

        
    #====================regular priest functions======================
    
    def priest_main(self):
        print("LOG: " + self.name + " is a priest")
        msg_from = self.new_message() #recieved msg from msg_from
        print("LOG: priest #" + self.name + " recieved msg from #" + str(msg_from))
        self.last_vote(msg_from)
        
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
        self.messenger.send_last_vote(last_voted, leader_num)
        #TODO: if responded, set promise to 1 for the relevant maxVote in the ledger 
        

    def vote():
        pass

        #choose (randomly) whether or not to vote on this ballot

        #send the vote to the leader (maybe put another function "voted")

    def on_success():
        pass
        #do something if the messenger brings the good news of a ballot success

    #======================general functions============================
        
    def new_message(self):
        #block till new message read
                
        while True:
            time.sleep(0.4)
            try:
                msgbook_data = pd.read_csv(self.messagebook)              
                if(msgbook_data.shape[0]>self.messages_recieved):
                    return msgbook_data.at[msgbook_data.shape[0]-1,'from']
            
            except pd.errors.EmptyDataError:
                pass

    

if __name__ == '__main__':
    god_instance = god(3,5)
