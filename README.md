# Simple Paxos
### Python implementation of part-time parliament consensus system used on the Greek island of Paxos, found during extensive archeological digs by L. Lamport

#### Documentation ripped from code

##### Formats

###### Ledger format
ballot number, decree
n,d

###### Messagebook format
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

##### Misc

###### Sequence of function writing (follow this when evaluating):

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

###### TODO
- multiple god instance support
- actually satisfy B1

###### TODO future: 
- split classes into different files for readability
- implement priest promise after lastvote (one idea: priest send a message to himself. this would require a new field in messagebook: 'outgoing/self')

###### TODO far future: 
- change communications between priests to socket communications instead of file io

##### God
- paxons are very religious; god controls anything and everything 
- literally creates priests ie initializes the objects 

##### Messenger
- messenger relays messages to and from the leader and the priest
she accomplishes this by tracking the priests' ledger files for changes
- each priest (including the leader) has a personal messenger (instance)

##### Priest
- priests are present (or not present) and vote (or not vote) for ballots proposed by the leader 
- they record all ballots they have participated in in individual ledger files
