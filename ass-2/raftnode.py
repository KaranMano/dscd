from pathlib import Path
from enum import Enum
import sys

sys.path.append("./proto")
import node_pb2_grpc
from log import RaftLog

RAFT_PORT = "8888"


class NodeState(Enum):
    LEADER = 0
    FOLLOWER = 0
    CANDIDATE = 0

class RaftNode:
    ID = None
    ip = None
    initialized = False
    log = None
    currentTerm = 0
    votedFor = None
    commitLength = 0
    currentRole = NodeState.FOLLOWER
    currentLeader = None
    votesReceived = set()
    sentLength = 0
    ackedLength = 0

    def __init__(self, ID, ip):
        self.ID = ID
        self.ip = ip
        Path(f"./logs/logs_node_{ID}").mkdir(parents=True, exist_ok=True)
        self.metadataFilePath = f"./logs/logs_node_{ID}/metadata.txt"
        self.logFilePath = f"./logs/logs_node_{ID}/logs.txt"

        if Path(self.metadataFilePath).exists():
            with open(self.metadataFilePath, "r") as metadata:
                self.currentTerm, self.votedFor, self.commitLength = (
                    metadata.readline().split()
                )

        log = RaftLog(self.logFilePath)

    def __set_attr__(self, name, value):
        if self.initialized:
            if name in ["currentTerm", "votedFor", "commitLength"]:
                with open(self.metadataFilePath, "w") as metadata:
                    metadata.write(
                        "{self.currentTerm} {self.votedFor} {self.commitLength}"
                    )
            else:
                raise AttributeError(
                    f"RaftNode does not allow assignment to .{name} member"
                )

    def startElection(self, nodes: dict):
        self.currentTerm += +1
        self.currentRole = NodeState.CANDIDATE
        self.votedFor = self.ID
        self.votesReceived.add(self.ID)
        lastTerm = 0
        if len(self.log) > 0:
            lastTerm = self.log[len(self.log) - 1]["term"]
        #! create message msg = ("VoteRequest", currNode.id, currentTerm, log.length, lastTerm)
        for node in nodes:
            pass
            #! send rpc
        #! start election timer


def handleStartElectionRPC():
    pass
    # on receiving (VoteRequest, cId, cTerm, cLogLength, cLogTerm)
    # at node nodeId do
    # if cTerm > currentTerm then
    # currentTerm := cTerm; currentRole := follower
    # votedFor := null
    # end if
    # lastTerm := 0
    # if log.length > 0 then lastTerm := log[log.length − 1].term; end if
    # logOk := (cLogTerm > lastTerm) ∨
    # (cLogTerm = lastTerm ∧ cLogLength ≥ log.length)
    # if cTerm = currentTerm ∧ logOk ∧ votedFor ∈ {cId, null} then
    # votedFor := cId
    # send (VoteResponse, nodeId, currentTerm,true) to node cId
    # else
    # send (VoteResponse, nodeId, currentTerm, false) to node cId
    # end if
    # end on


def receiveVoteResponse():
    pass
    # on receiving (VoteResponse, voterId, term, granted) at nodeId do
    # if currentRole = candidate ∧ term = currentTerm ∧ granted then
    # votesReceived := votesReceived ∪ {voterId}
    # if |votesReceived| ≥ d(|nodes| + 1)/2e then
    # currentRole := leader; currentLeader := nodeId
    # cancel election timer
    # for each follower ∈ nodes \ {nodeId} do
    # sentLength[follower ] := log.length
    # ackedLength[follower ] := 0
    # ReplicateLog(nodeId, follower )
    # end for
    # end if
    # else if term > currentTerm then
    # currentTerm := term
    # currentRole := follower
    # votedFor := null
    # cancel election timer
    # end if
    # end on


def broadcast():
    pass
    # on request to broadcast msg at node nodeId do
    # if currentRole = leader then
    # append the record (msg : msg, term : currentTerm) to log
    # ackedLength[nodeId] := log.length
    # for each follower ∈ nodes \ {nodeId} do
    # ReplicateLog(nodeId, follower )
    # end for
    # else
    # forward the request to currentLeader via a FIFO link
    # end if
    # end on
    # periodically at node nodeId do
    # if currentRole = leader then
    # for each follower ∈ nodes \ {nodeId} do
    # ReplicateLog(nodeId, follower )
    # end for
    # end if
    # end do


def replicate():
    pass
    # function ReplicateLog(leaderId, followerId)
    # prefixLen := sentLength[followerId]
    # suffix := hlog[prefixLen], log[prefixLen + 1], . . . ,
    # log[log.length − 1]i
    # prefixTerm := 0
    # if prefixLen > 0 then
    # prefixTerm := log[prefixLen − 1].term
    # end if
    # send (LogRequest, leaderId, currentTerm, prefixLen,
    # prefixTerm, commitLength, suffix ) to followerId
    # end function


def lofreq():
    pass
    # on receiving (LogRequest, leaderId, term, prefixLen, prefixTerm,
    # leaderCommit, suffix ) at node nodeId do
    # if term > currentTerm then
    # currentTerm := term; votedFor := null
    # cancel election timer
    # end if
    # if term = currentTerm then
    # currentRole := follower; currentLeader := leaderId
    # end if
    # logOk := (log.length ≥ prefixLen) ∧
    # (prefixLen = 0 ∨ log[prefixLen − 1].term = prefixTerm)
    # if term = currentTerm ∧ logOk then
    # AppendEntries(prefixLen, leaderCommit, suffix )
    # ack := prefixLen + suffix .length
    # send (LogResponse, nodeId, currentTerm, ack,true) to leaderId
    # else
    # send (LogResponse, nodeId, currentTerm, 0, false) to leaderId
    # end if
    # end on


def append():
    pass
    # function AppendEntries(prefixLen, leaderCommit, suffix )
    # if suffix .length > 0 ∧ log.length > prefixLen then
    # index := min(log.length, prefixLen + suffix .length) − 1
    # if log[index ].term 6= suffix [index − prefixLen].term then
    # log := hlog[0], log[1], . . . , log[prefixLen − 1]i
    # end if
    # end if
    # if prefixLen + suffix .length > log.length then
    # for i := log.length − prefixLen to suffix .length − 1 do
    # append suffix [i] to log
    # end for
    # end if
    # if leaderCommit > commitLength then
    # for i := commitLength to leaderCommit − 1 do
    # deliver log[i].msg to the application
    # end for
    # commitLength := leaderCommit
    # end if
    # end function


def logResponse():
    pass
    # on receiving (LogResponse, follower , term, ack, success) at nodeId do
    # if term = currentTerm ∧ currentRole = leader then
    # if success = true ∧ ack ≥ ackedLength[follower ] then
    # sentLength[follower ] := ack
    # ackedLength[follower ] := ack
    # CommitLogEntries()
    # else if sentLength[follower ] > 0 then
    # sentLength[follower ] := sentLength[follower ] − 1
    # ReplicateLog(nodeId, follower )
    # end if
    # else if term > currentTerm then
    # currentTerm := term
    # currentRole := follower
    # votedFor := null
    # cancel election timer
    # end if
    # end on


def commit():
    pass
    # define acks(length) = |{n ∈ nodes | ackedLength[n] ≥ length}|
    # function CommitLogEntries
    # minAcks := d(|nodes| + 1)/2e
    # ready := {len ∈ {1, . . . , log.length} | acks(len) ≥ minAcks}
    # if ready 6= {} ∧ max(ready) > commitLength ∧
    # log[max(ready) − 1].term = currentTerm then
    # for i := commitLength to max(ready) − 1 do
    # deliver log[i].msg to the application
    # end for
    # commitLength := max(ready)
    # end if
    # end functio


class NodeService(node_pb2_grpc.NodeServiceServicer):
    def AppendEntries():
        pass

    def RequestVote():
        pass
