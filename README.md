## Simple Paxos
#### Simple thread-based Python simulation of the [Part-time Parliament](https://dl.acm.org/citation.cfm?id=279229) consensus system used on the Greek island of Paxos

#### Documentation ripped from code

##### Formats

###### Ledger 
ballot number, decree
n,d

###### Messagebook 
(Priests will track these for changes by messengers)

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

##### Dev log

DONE

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

TODO
- Actually satisfy B1
- Multiple god instance support

TODO future: 
- Implement priest promise after lastvote (one idea: priest send a message to himself. this would require a new field in messagebook: 'outgoing/self')

TODO far future: 
- Change messages between priests to go through sockets instead of files

##### God
- Paxons are very religious; god controls anything and everything 
- Literally creates priests i.e. initializes the objects 

##### Messenger
- Messenger relays messages to and from the leader and the priest
- She accomplishes this by tracking the priests' ledger files for changes
- Each priest (including the leader) has a personal messenger (instance)

##### Priest
- Priests are present (or not present) and vote (or not vote) for ballots proposed by the leader 
- They record all ballots they have participated in in individual ledger files
