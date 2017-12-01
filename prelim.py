"""
priest ledger format
-------------------
front #denotes the start of the actual ledger 
0/1,n,0/1  #voted or not, ballot number, promised or not 
promised or not explanation:       whether or not this priest has promised to not 
                                   respond to maxvote requests after this ballot

"""

"""
paxons are very religious; god controls anything and everything and the synod ritual
lies in that domain (of anything and everything, that is)
- literally creates leaders and priests ie initializes the objects 
- assigns ballot number ranges for each priest (so B1 is satisfied)
"""    
class god:


"""
messenger relays messages to and from the leader and the priest
she accomplishes this by tracking the priests' ledger files for changes

each priest (including the leader) has a personal messenger 
"""
class messenger(god):

    """
    leader messenger functions
    """
    def send_next_ballot():

    def send_begin_ballot():

    def send_on_success():
        
    """
    priest messenger functions
    """
    def send_last_vote():

    def send_vote():
        

        
"""
priests are present (or not present) and vote (or not vote) for ballots proposed 
by the leader 
they record all ballots they have participated in in individual ledger files
"""    
class priest(god):

    def __init__(self, name):
        self.name = name #write this name in the ledger in case it gets lost (ledger fileaname)

    def last_vote():
        #responding to a next_ballot request from the leader        
        #determine the lastVote and send it to the leader (if not promised to another leader) (might
        #need another function for this)

        #if responded, set promise to 1 for the relevant maxVote in the ledger

    def vote():
        #choose (randomly) whether or not to vote on this ballot

        #send the vote to the leader (another function "voted"?)

    def on_success():
        #do something if the messenger brings the good news of a ballot success
        
class leader(god):
    
    def __init__(self, ballot_num):
        self.ballot_num = ballot_num;
        
    def next_ballot(ballot_num):
        #randomly choose a majority set of priests
        
        #send the nextBallot message to the priests and wait for their responses 

    def begin_ballot():
        #send message to every priest indicating that his vote is requested

    def evaluate():
        #check if the ballot was a success and note the decree if it was

        #send the sucess message to all living priests
    
    
    
