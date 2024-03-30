from defs import *
from pathlib import Path
from enum import Enum
import json
import copy
import node_pb2_grpc
import node_pb2
import grpc
import asyncio
import logging
import math
import traceback
import inspect
logger = logging.getLogger(__name__)

class Context():
    # magic functions
    def __init__(self, ID, ip, port, nodes):
        # default values
        # private to track initialization
        self._initialized = False
        
        # all nodes in the system
        self.nodes = None

        # metadata
        self.ID = None
        self.ip = None
        self.port = None
        
        # persistent external storage
        self.log = None
        self.db = None

        # persistent metadata
        self.currentTerm = 0 
        self.votedFor = None
        self.commitLength = 0

        # non peristent metadata
        self.hasLeaderLease = False
        self.leaseWait = {"end": 0, "max": 0}
        self.currentRole = NodeStates.FOLLOWER
        self.currentLeader = None
        self.votesReceived = set()
        self.sentLength = []
        self.ackedLength = []
        self.electionTimer = None
        self.heartbeatTimer = None
        self.leaseTimer = None

        # async task management
        self.channels = {}
        self.tasks = [] 
        self.tasksMetadata = []
        
        #init
        logger.info(f"Initializing Node {ID} at {ip}:{port}")

        self.nodes = nodes
        
        self.ID = int(ID)
        self.ip = ip
        self.port = port

        self.sentLength = [0 for _ in range(len(self.nodes))]
        self.ackedLength = [0 for _ in range(len(self.nodes))]

        Path(f"./logs_node_{ID}").mkdir(parents=True, exist_ok=True)
        self.db = Database(ID)
        self.logFilePath = f"./logs_node_{ID}/logs.txt"
        self.log = RaftLog(self.logFilePath)
        self.metadataFilePath = f"./logs_node_{ID}/metadata.txt"
        if Path(self.metadataFilePath).exists():
            with open(self.metadataFilePath, "r") as metadata:
                self.currentTerm, self.votedFor, self.commitLength = json.load(metadata)

        self.electionTimer = TimedCallback([ELECTION_INTERVAL - 2, ELECTION_INTERVAL + 2], self._startElection, None)
        self.heartbeatTimer = TimedCallback(HEARTBEAT_INTERVAL, self._heartbeat, None)
        self.leaseTimer = TimedCallback(LEASE_INTERVAL, self._acquireLease, None)
        self.electionTimer.reset()
        self.heartbeatTimer.reset()
        self.leaseTimer.reset()
        
        self._initialized = True

    def __setattr__(self, name, value):
        if "_initialized" in self.__dict__ and self._initialized:
            if name in ["_initialized", "log"]:
                raise AttributeError(f"State does not allow assignment to .{name} member")
            
            self.__dict__[name] = value
            if name in ["currentTerm", "votedFor", "commitLength"]:
                with open(self.metadataFilePath, "w") as metadata:
                    json.dump([self.currentTerm, self.votedFor, self.commitLength], metadata)
        else:
            self.__dict__[name] = value

    # util
    def acks(self, length):
        numberOfAcks = 0
        for nodeID in range(len(self.nodes)):
            if self.ackedLength[nodeID] >= length:
                numberOfAcks += 1
        return numberOfAcks

    def getChannel(self, addr):
        channel = None
        if  addr in self.channels:
            channel  = self.channels[addr]
        else:
            channel = self.channels[addr] = grpc.aio.insecure_channel(addr)
        return channel

    async def rpcWrapper(self, call, request):
        try:
            return await call(request)
        except BaseException:
            raise

    # timer callbacks
    def _acquireLease(self):
        if self.currentRole == NodeStates.LEADER and not self.hasLeaderLease and self.leaseWait["end"] < time.time():
            logger.info(f"[LEASE] : Node {self.ID} acquired the leader for term {self.currentTerm}.")
            self.hasLeaderLease = True
        elif self.currentRole != NodeStates.LEADER and self.hasLeaderLease:
            logger.info(f"[LEASE] : Leader {self.ID} lease renewal failed, stepping down.")
            self.hasLeaderLease = False
        self.leaseTimer.reset()

    def _heartbeat(self):
        if self.currentRole == NodeStates.LEADER:
            logger.info(f"[HEARTBEAT] : Leader {self.ID} sending heartbeat & Renewing Lease")
            for nodeID, node in enumerate(self.nodes):
                if nodeID == self.ID:
                    continue
                self.replicateLog(nodeID)
        self.heartbeatTimer.reset()

    def _startElection(self):
        logger.info(f"[ELECTION] : Node {self.ID} election timer timed out, Starting election.")
        self.currentTerm += 1
        self.currentRole = NodeStates.CANDIDATE
        self.votedFor = self.ID 
        self.votesReceived.add(self.ID) 
        lastTerm = 0
        if len(self.log) > 0:
            lastTerm = self.log[len(self.log) - 1]["term"]
        request = node_pb2.VoteRequest(term=self.currentTerm, candidateId=self.ID, lastLogIndex=len(self.log), lastLogTerm=lastTerm)
        for nodeID, node in enumerate(self.nodes):
            if nodeID == self.ID:
                continue
            channel = self.getChannel(f"{node[0]}:{node[1]}")
            stub = node_pb2_grpc.NodeStub(channel)
            self.tasks.append(asyncio.create_task(self.rpcWrapper(stub.RequestVote, request)))
            self.tasks[-1].add_done_callback(self.collectVote)
            self.tasksMetadata.append(nodeID)
        self.electionTimer.reset()

    # Log update and commit functions
    def commitLogEntries(self):
        minAcks = math.ceil(float(len(self.nodes) + 1)/2.0)
        ready = [i+1 for i in range(len(self.log)) if self.acks(i) >= minAcks]
        if len(ready) != 0 and max(ready) > self.commitLength and self.log[max(ready) - 1]["term"] == self.currentTerm:
            logger.info(f"[LOG] : Committing entries")
            for i in range(self.commitLength, max(ready)):
                if self.log[i]["msg"].split()[0] == "SET":
                    _, key, value = self.log[i]["msg"].split()
                    logger.info(f"[LOG] Node {self.ID} {self.currentRole.name} committed the entry [{key} {value}] to the state machine.")
                    self.db.commit(key, value)
            self.commitLength = max(ready)

    def appendEntries(self, prefixLen, leaderCommit, suffix):
        logger.info(f"[LOG] : Append entries")
        if len(suffix) > 0 and len(self.log) > prefixLen:
            index = min(len(self.log), prefixLen + len(suffix)) - 1
            if self.log[index]["term"] != suffix[index - prefixLen]["term"]:
                self.log.clearAfter(prefixLen)
        if prefixLen + len(suffix) > len(self.log):
            for i in range(len(self.log) - prefixLen, len(suffix)):
                self.log.appendAt(suffix[i]["msg"], suffix[i]["term"], len(self.log))
        if leaderCommit > self.commitLength:
            for i in range(self.commitLength, leaderCommit):
                if self.log[i]["msg"].split()[0] == "SET":
                    _, key, value = self.log[i]["msg"].split()
                    self.db.commit(key, value)
            self.commitLength = leaderCommit

    def replicateLog(self, followerID):
        logger.info(f"[LOG] : Replicating log")
        prefixLen = self.sentLength[followerID]
        suffix = self.log[prefixLen:]
        prefixTerm = 0
        if prefixLen > 0:
            prefixTerm = self.log[prefixLen - 1]["term"]
        
        channel = self.getChannel(f"{self.nodes[followerID][0]}:{self.nodes[followerID][1]}")
        stub = node_pb2_grpc.NodeStub(channel)
        entries = [node_pb2.Entry(msg=entry["msg"], term=entry["term"]) for entry in suffix]
        request = node_pb2.AppendRequest(
            term=self.currentTerm, leaderID=self.ID, prevLogIndex=prefixLen, prevLogTerm=prefixTerm, entries=entries, leaderCommitIndex=self.commitLength
        )
        self.tasks.append(asyncio.create_task(self.rpcWrapper(stub.AppendEntries, request)))
        self.tasks[-1].add_done_callback(self.processLogResponse)
        self.tasksMetadata.append(followerID)

    def processLogResponse(self, task):
        taskIndex = self.tasks.index(task)
        followerID = self.tasksMetadata[taskIndex]
        try:
            response = task.result()
            logger.info(f"[LOG] : Processing appendentries rpc response")
            if response.term == self.currentTerm and self.currentRole == NodeStates.LEADER:
                if response.success == True and response.ackIndex >= self.ackedLength[response.nodeID]:
                    self.sentLength[response.nodeID ] = response.ackIndex
                    self.ackedLength[response.nodeID ] = response.ackIndex
                    self.commitLogEntries()
                elif self.sentLength[response.nodeID] > 0:
                    self.sentLength[response.nodeID] = self.sentLength[response.nodeID ] - 1
                    self.replicateLog(response.nodeId)
            elif response.term > self.currentTerm:
                self.currentTerm = response.term
                self.currentRole = NodeStates.FOLLOWER
                self.votedFor = None
                self.electionTimer.reset()
        except grpc.aio.AioRpcError as e:
            logger.info(f"[LOG] : Error occurred while sending RPC to Node {followerID}. {e.__class__.__name__}")
        except BaseException as e:
            logger.info(f"Error occurred while appending entries, {e.__class__.__name__}")
            logger.info(traceback.format_exc())
        finally:
            self.tasksMetadata = self.tasksMetadata[:taskIndex] + self.tasksMetadata[taskIndex+1:]
            self.tasks.remove(task)
            

    # Election functions            
    def collectVote(self, task):
        taskIndex = self.tasks.index(task)
        followerID = self.tasksMetadata[taskIndex]
        try:
            response = task.result()
            logger.info(f"[ELECTION] : Processing RequestVote RPC response")
            if self.currentRole == NodeStates.CANDIDATE and response.term == self.currentTerm and response.voteGranted:
                logger.info(f"[ELECTION] : Received vote from {response.resID}")
                self.votesReceived.add(response.resID)
                self.leaseWait["max"] = max(self.leaseWait["max"] , response.leaseLeft)
            if len(self.votesReceived) >= math.ceil(float(len(self.nodes) + 1)/2.0):
                logger.info(f"[ELECTION] : Node {self.ID} became the leader for term {self.currentTerm}.")
                self.currentRole = NodeStates.LEADER 
                self.currentLeader = self.ID
                self.electionTimer.stop()
                self.leaseWait["end"] = time.time() + self.leaseWait["max"] 
                self.hasLeaderLease = False
                logger.info(f"[LEASE] Will wait for {self.leaseWait['max']} which will end at {self.leaseWait['end']} before acquiring lease")
                for nodeID, node in enumerate(self.nodes):
                    if node == [self.ip, self.port]:
                        continue
                    self.sentLength[nodeID] = len(self.log)
                    self.ackedLength[nodeID] = 0
                    self.replicateLog(nodeID)
            elif response.term > self.currentTerm:
                logger.info(f"[ELECTION] : Node {self.ID} Stepping down")
                self.currentTerm = response.term
                self.currentRole = NodeStates.FOLLOWER
                self.votedFor = None
                self.electionTimer.reset()
                self.leaseWait["max"] = 0
        except grpc.aio.AioRpcError as e:
            logger.info(f"[ELECTION] : Error occurred while sending RPC to Node {followerID}. {e.__class__.__name__}")
        except BaseException as e:
            logger.info(f"Error occurred while collecting vote. {e.__class__.__name__}")
            # logger.info(traceback.format_exc())
        finally:
            self.tasksMetadata = self.tasksMetadata[:taskIndex] + self.tasksMetadata[taskIndex+1:]
            self.tasks.remove(task)

    # Client functions
    def set(self, key, value):
        logger.info(f"[CLIENT] : Node {self.ID} {self.currentRole} received a SET request")    # similarly log GET
        self.log.appendAt(f"SET {key} {value}", self.currentTerm, len(self.log))
        self.ackedLength[self.ID] = len(self.log)
        for nodeID, node in enumerate(self.nodes):
            if node == [self.ip, self.port]:
                continue
            self.replicateLog(nodeID)        
    
