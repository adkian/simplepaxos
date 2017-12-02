import pandas as pd
import random as rand
import string

"""
===============================

priest ledger format:
voted or not, ballot number, promised or not, times led
0/1,n,0/1,x  

promised or not explanation:       whether or not this priest has promised to not 
                                   respond to maxvote requests after this ballot
times led explanation:             number of times she's been leader
                                   (see doc for messenger)
===============================

priest messagebook format: 
(priests will track these for changes by messenger)

from,code
n,1/2/3

codes (not leader): 
1: next ballot
2: begin ballot
3: successful ballot

codes (leader):

===============================

sequence of code writing (may provide intuition for future folks):
- skeleton
- priest init
- leader_main
- god init
- next_ballot
- send_next_ballot
===============================
"""



"""
paxons are very religious; god controls anything and everything 

- literally creates priests ie initializes the objects 
- assigns ballot number ranges for each priest (so B1 is satisfied)
"""    
class god:
    
    num_priests = 0
    priests = {}
    
    def __init__(self, num_priests, num_ballots, offset=100): 
        self.num_priests = num_priests
        self.num_ballots = num_ballots
        
        #create and name the priests (quite godly)
        for x in range(0, self.num_priests):
            self.priests[x] = priest(name, (x+1)*offset)            
        

"""
messenger relays messages to and from the leader and the priest
she accomplishes this by tracking the priests' ledger files for changes

each priest (including the leader) has a personal messenger (instance)
"""

class messenger(god):

    """
    leader messenger functions
    """
    def send_next_ballot(current_list, ballot_num):
        pass
        

    def send_begin_ballot():
        pass
    
    def send_on_success():
        pass
        
    """
    priest messenger functions
    """
    def send_last_vote():
        pass

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
class priest(messenger):
        
    def __init__(self, name, start_offset):
        
        self.name = name #write this name in the ledger in case it gets lost (ledger fileaname)
        self.messenger = messenger() #hire a messenger
        self.ledger = open("ledgers/" + self.name, "+")
        self.offset = offset                    

    #=====================leader functions===================
    def leader_main():
        times_led = self.ledger.at[self.ledger.shape[0]-1,'times_led'] #last col of last row of ledger
        ballot_num = self.offset + times_led #B1 is satisfied assuming num_ballots < difference between offsets
        
        self.next_ballot(ballot_num)
        self.begin_ballot()
        
    def next_ballot(ballot_num):
        #randomly choose a number of priests: 40% - 100% of total priests
        rand_num = random.randrange(num_priests*0.4, num_priests+1)       
        current_priests = random.sample(priests.keys(), rand_num)        
        
        #Send the nextBallot message to the priests and wait for their responses
        messenger.send_next_ballot(current_list, ballot_num)

    def begin_ballot():
        #wait for all threads to respond
        #send message to every priest indicating that his vote is requested

    def evaluate():
        pass
        #check if the ballot was a success and note the decree if it was

        #send the sucess message to all living priests

        
    #====================regular priest functions======================
    def priest_main():
        pass
    
    def last_vote():
        pass
        #responding to a next_ballot request from the leader        
        #determine the lastVote and send it to the leader (if not promised to another leader) (might
        #need another function for this)        
        
        #if responded, set promise to 1 for the relevant maxVote in the ledger

    def vote():
        pass
        #choose (randomly) whether or not to vote on this ballot

        #send the vote to the leader (another function "voted"?)

    def on_success():
        pass
        #do something if the messenger brings the good news of a ballot success
    
    
    
