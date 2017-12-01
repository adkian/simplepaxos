"""
priest ledger format
-------------------
front #denotes the start of the actual ledger 
0/1,n,0/1,x  #voted or not, ballot number, promised or not, adder multiplier
promised or not explanation:       whether or not this priest has promised to not 
                                   respond to maxvote requests after this ballot
adder multiplier explanation:      (see doc for messenger)

"""

"""
paxons are very religious; god controls anything and everything and the synod ritual
lies in that domain (of anything and everything, that is)
- literally creates leaders and priests ie initializes the objects 
- assigns ballot number ranges for each priest (so B1 is satisfied)
"""    
class god:
    pass

"""
messenger relays messages to and from the leader and the priest
she accomplishes this by tracking the priests' ledger files for changes

each priest (including the leader) has a personal messenger 
"""

class messenger():

    """
    leader messenger functions
    """
    def send_next_ballot():
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

note: unique sets of numbers are created by an 'adder': starting from a base value, 
each priest determines next ballot number by adding adder*x where x is the number of 
ballots he's assigned numbers before the current ballot
"""    
class priest(god, messenger):
        
    def __init__(self, name, is_leader, adder):
        self.name = name #write this name in the ledger in case it gets lost (ledger fileaname)
        self.is_leader = is_leader
        self.messenger = messenger() #hire a messenger
        self.adder = adder
        self.ledger = open("ledgers/" + self.name, "+")
        
        #if(self.is_leader):
            
            

    #====================regular priest functions======================
        
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

    #=====================leader functions===================
    def next_ballot(ballot_num):
        pass
        #randomly choose a majority set of priests
        
        #send the nextBallot message to the priests and wait for their responses 

    def begin_ballot():
        pass
        #send message to every priest indicating that his vote is requested

    def evaluate():
        pass
        #check if the ballot was a success and note the decree if it was

        #send the sucess message to all living priests
    
    
    
    
    
