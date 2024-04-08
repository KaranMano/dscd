from pathlib import Path
from enum import Enum
from datetime import datetime
import sys
import node_pb2_grpc
import node_pb2
import grpc
import asyncio
import logging
import random
import json
logger = logging.getLogger(__name__)
import copy
import time

ELECTION_INTERVAL = [5, 10]
HEARTBEAT_INTERVAL = 1
LEASE_INTERVAL = 6

def loadNodes():
    nodes = []
    with open("nodes.txt", "r") as nodeRegistry:
        next(nodeRegistry)
        for entry in nodeRegistry:
            ID, ip, port = entry.split()
            nodes.append([ip, port])
    return nodes

def getCurrentTimeStr():
    return (datetime.now()).strftime("%H:%M:%S")

class NodeStates(Enum):
    LEADER = 0
    FOLLOWER = 1
    CANDIDATE = 2

class TimedCallback():
    def __init__(self, duration, callback, data):
        self.data = data
        self.callback = callback
        self.duration = duration
        self.runningTask = None
        self.end = None
        
        if isinstance(self.duration, list) and len(self.duration) == 2:
            self.timeout = lambda duration: random.random() * (duration[1] - duration[0]) + duration[0]
        elif isinstance(self.duration, int):
            self.timeout = lambda duration: duration
        else: 
            raise Exception("Invalid duration provided")

    async def callAfterDuration(self):
        timeout = self.timeout(self.duration)
        self.end = time.time() + timeout
        await asyncio.sleep(timeout)
        if self.data:
            self.callback(self.data)
        else:
            self.callback()

    def getTimeLeft(self):
        if self.end == None:
            return 0
        return max(0, self.end - time.time())

    def reset(self):
        self.stop()
        self.runningTask = asyncio.create_task(self.callAfterDuration())

    def stop(self):
        if self.runningTask and not self.runningTask.done():
            self.runningTask.cancel()

    def setDuration(self, duration):
        self.duration = duration
        if isinstance(self.duration, list) and len(self.duration) == 2:
            self.timeout = lambda duration: random.random() * (duration[1] - duration[0]) + duration[0]
        elif isinstance(self.duration, int):
            self.timeout = lambda duration: duration
        else: 
            raise Exception("Invalid duration provided")
        
class Database():
    # node - current Node. Used to resolve path to db file
    def __init__(self, ID):
        self.record = {}
        Path(f"./logs_node_{ID}").mkdir(parents=True, exist_ok=True)
        self.filePath = f"./logs_node_{ID}/db.txt"
        if Path(self.filePath).exists():
            with open(self.filePath, "r") as db:
                self.record = json.load(db)
    
    def __getitem__(self, key):
        if key in self.record:
            data =  copy.copy(self.record[key])
        else:
            data = ""
        return data

    def commit(self, key, value):
        self.record[key] = value
        with open(self.filePath, "w") as db:
            json.dump(self.record, db)

class RaftLog():
    def __init__(self, logFilePath):
        self.raw = []
        self.index = 0
        self.logFilePath = logFilePath
        if Path(self.logFilePath).exists():
            with open(self.logFilePath, "r") as log:
                self.raw = json.load(log)
    def __len__(self):
        return len(self.raw)
    def __iter__(self):
        return self
    def __next__(self):
        try:
            result = copy.copy(self.raw[self.index])
        except IndexError:
            self.index = 0
            raise StopIteration
        self.index += 1
        return result
    def __getitem__(self, key):
        return copy.copy(self.raw[key])

    def __set_attr__(self, name, value):
        raise KeyError
    
    def appendAt(self, msg, term, index):
        self.raw = self.raw[:index]
        self.raw.append({"msg": msg, "term": term})

        with open(self.logFilePath, "w") as log:
            json.dump(self.raw, log)

    def clearAfter(self, index):
        self.raw = self.raw[:index]

class NodeServicer(node_pb2_grpc.ClientServicer):
    def __init__(self, state):
        self.state = state
    
    async def AppendEntries(self, request, context):
        logger.info(f"[LOG] : Append entries rpc from {request.leaderID}")
        if request.term > self.state.currentTerm:
            self.state.currentTerm = request.term 
            self.state.votedFor = None
            self.state.electionTimer.stop()
        if request.term == self.state.currentTerm:
            self.state.currentRole = NodeStates.FOLLOWER 
            self.state.currentLeader = request.leaderID
            self.state.electionTimer.reset()
        logOk = (len(self.state.log) >= request.prevLogIndex) and (request.prevLogIndex == 0 or self.state.log[request.prevLogIndex - 1]["term"] == request.prevLogTerm)
        if request.term == self.state.currentTerm and logOk:
            self.state.leaseTimer.reset()
            self.state.heartbeatTimer.reset()
            self.state.electionTimer.reset()
            self.state.appendEntries(request.prevLogIndex, request.leaderCommitIndex, [{"msg": entry.msg, "term": entry.term} for entry in request.entries])
            ack = request.prevLogIndex + len(request.entries)
            logger.info(f"[LOG] : Node {self.state.ID} accepted AppendEntries RPC from {request.leaderID}")
            return node_pb2.AppendResponse(nodeID=self.state.ID, ackIndex=ack, term=self.state.currentTerm, success=True)
        else:
            logger.info(f"[LOG] : Node {self.state.ID} rejected AppendEntries RPC from {request.leaderID}")
            return node_pb2.AppendResponse(nodeID=self.state.ID, ackIndex=0, term=self.state.currentTerm, success=False)
    
    async def RequestVote(self, request, context):
        logger.info(f"[ELECTION] : RequestVote RPC from {request.candidateId}")
        if self.state.currentRole != NodeStates.LEADER:
            self.state.electionTimer.reset()
        if request.term > self.state.currentTerm:
            self.state.currentTerm = request.term
            self.state.currentRole = NodeStates.FOLLOWER
            self.state.votedFor = None
        lastTerm = 0
        if len(self.state.log) > 0:
            lastTerm = self.state.log[len(self.state.log) - 1]["term"]
        logOk = (request.lastLogTerm > lastTerm) or (request.lastLogTerm == lastTerm and request.lastLogIndex >= len(self.state.log))
        if request.term == self.state.currentTerm and logOk and self.state.votedFor in [request.candidateId, None]:
            logger.info(f"[ELECTION] : Vote granted for Node {request.candidateId} in term {request.term}")
            self.state.leaseTimer.reset()
            self.state.heartbeatTimer.reset()
            self.state.votedFor = request.candidateId
            return node_pb2.VoteResponse(resID=self.state.ID ,term=self.state.currentTerm, voteGranted=True, leaseLeft=self.state.heartbeatTimer.getTimeLeft())
        else:
            logger.info(f"[ELECTION] : Vote denied for Node {request.candidateId} in term {request.term}")
            return node_pb2.VoteResponse(resID=self.state.ID ,term=self.state.currentTerm, voteGranted=False, leaseLeft=self.state.heartbeatTimer.getTimeLeft())

class ClientServicer(node_pb2_grpc.ClientServicer):
    def __init__(self, state):
        self.state = state

    async def ServeClient(self, request, context):
        logger.info(f"[CLIENT] : Client request {request.request}")
        command, *item = list(map(lambda x: x.strip(), request.request.split(",")))
        if command == "GET":
            if self.state.hasLeaderLease:
                return node_pb2.ServeClientReply(data=self.state.db[item[0]], leaderID=self.state.currentLeader, success=True)
            else:
                return node_pb2.ServeClientReply(data="", leaderID=self.state.currentLeader, success=False)
        elif command == "SET":
            if self.state.currentRole == NodeStates.LEADER and self.state.hasLeaderLease and self.state.hasWritePermission:
                self.state.set(*item)
                return node_pb2.ServeClientReply(data="", leaderID=self.state.currentLeader, success=True)
            else:
                return node_pb2.ServeClientReply(data="", leaderID=self.state.currentLeader, success=False)
        else:
            logger.info(f"[CLIENT] : Incorrect command syntax")
