from pathlib import Path
from enum import Enum
import json
import copy
import node_pb2_grpc
import node_pb2
import grpc
import asyncio
import logging
import random
logger = logging.getLogger(__name__)

ELECTION_INTERVAL = 10
HEARTBEAT_INTERVAL = 6
LEASE_INTERVAL = 10

class NodeStates(Enum):
    LEADER = 0
    FOLLOWER = 1
    CANDIDATE = 2

class TimedCallback():
    def __init__(self, duration, callback, data):
        logger.info(f"Initial start of timer for {callback.__name__}")
        self.data = data
        self.callback = callback
        self.duration = duration
        
        if isinstance(self.duration, list) and len(self.duration) == 2:
            self.timeout = lambda duration: random.random() * (duration[1] - duration[0]) + duration[0]
        elif isinstance(self.duration, int):
            self.timeout = lambda duration: duration
        else: 
            raise Exception("Invalid duration provided")

        self.runningTask = asyncio.create_task(self.callAfterDuration())

    async def callAfterDuration(self):
        logger.info(f"Timer started for {self.callback.__name__} for {self.duration} seconds")
        await asyncio.sleep(self.timeout(self.duration))
        logger.info(f"Running callback {self.callback.__name__}")
        if self.data:
            self.callback(self.data)
        else:
            self.callback()

    def reset(self):
        logger.info(f"Reseting timer for {self.callback.__name__}")
        self.stop()
        self.runningTask = asyncio.create_task(self.callAfterDuration())

    def stop(self):
        logger.info(f"Stopping timer for {self.callback.__name__}")
        if self.runningTask and not self.runningTask.done():
            self.runningTask.cancel()

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
        return copy.copy(self.record[key])

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
        raw = raw[:index]
        raw.append({"msg": msg, "term": term})

        with open(self.logFilePath, "w") as log:
            json.dump(self.raw, log)

    def clearAfter(self, index):
        raw = raw[:index]

class NodeServicer(node_pb2_grpc.ClientServicer):
    def __init__(self, state):
        self.state = state
    
    def AppendEntries(self, request, context):
        logger.info(f"Append entries rpc from {request.leaderID}")
        if request.term > self.state.currentTerm:
            self.state.currentTerm = request.term 
            self.state.votedFor = None
            self.state.electionTimer.reset()
        if request.term == self.state.currentTerm:
            self.state.currentRole = NodeStates.FOLLOWER 
            self.state.currentLeader = request.leaderID
        logOk = (len(self.state.log.length) >= request.prevLogIndex) and (request.prevLogIndex == 0 or self.state.log[request.prevLogIndex - 1]["term"] == request.prevLogTerm)
        if request.term == self.state.currentTerm and logOk:
            self.state.appendEntries(request.prevLogIndex, request.leaderCommitIndex, request.suffix)
            ack = request.prevLogIndex + len(request.entries)
            return node_pb2.AppendResponse(nodeID=self.state.ID, ackIndex=ack, term=self.state.currentTerm, success=True)
        else:
            return node_pb2.AppendResponse(nodeID=self.state.ID, ackIndex=0, term=self.state.currentTerm, success=False)
    
    def RequestVote(self, request, context):
        logger.info(f"RequestVote RPC from {request.candidateId}")
        if request.term > self.state.currentTerm:
            self.state.currentTerm = request.term
            self.state.currentRole = NodeStates.FOLLOWER
            self.state.votedFor = None
        lastTerm = 0
        if len(self.state.log) > 0:
            lastTerm = self.state.log[len(self.state.log) - 1]["term"]
        logOk = (request.lastLogTerm > lastTerm) or (request.lastLogTerm == lastTerm and request.lastLogIndex >= len(self.state.log))
        if request.term == self.state.currentTerm and logOk and self.state.votedFor in [request.candidateId, None]:
            logger.info(f"Granting vote to {request.candidateId}")
            self.state.votedFor = request.candidateId
            return node_pb2.VoteResponse(resID=self.state.ID ,term=self.state.currentTerm, voteGranted=True)
        else:
            logger.info(f"Rejecting vote request from {request.candidateId}")
            return node_pb2.VoteResponse(resID=self.state.ID ,term=self.state.currentTerm, voteGranted=False)

class ClientServicer(node_pb2_grpc.ClientServicer):
    def __init__(self, state):
        self.state = state

    def ServeClient(self, request, context):
        logger.info(f"Client request {request.request}")
        command, *item = request.request.split(",")
        if command == "GET":
            if self.state.currentRole == NodeStates.LEADER and self.state.hasLeaderLease:
                return node_pb2.ServeClientReply(data=self.state.db[item[0]], leaderID=str(self.state.currentLeader), success=True)
            else:
                return node_pb2.ServeClientReply(data="", leaderID=str(self.state.currentLeader), success=False)
        elif command == "SET":
            if self.state.currentRole == NodeStates.LEADER and self.state.hasLeaderLease:
                self.state.set(*item)
                return node_pb2.ServeClientReply(data="", leaderID=str(self.state.currentLeader), success=True)
            else:
                return node_pb2.ServeClientReply(data="", leaderID=str(self.state.currentLeader), success=False)
        else:
            raise ValueError("Command syntax incorrect")
