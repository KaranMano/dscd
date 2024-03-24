from pathlib import Path
from enum import Enum
import json
import copy

RAFT_PORT = "8888"

class NodeStates(Enum):
    LEADER = 0
    FOLLOWER = 0
    CANDIDATE = 0

def Node():
    def __init__(self, name, ip):
        self.name = name
        self.ip = ip

def DataBase():
    record = {}

    # node - current Node. Used to resolve path to db file
    def __init__(self, node):
        Path(f"./logs_node_{node.id}").mkdir(parents=True, exist_ok=True)
        self.filePath = f"./logs_node_{node.id}/db.txt"
        with open(self.filePath, "r") as db:
            self.record = json.load(db)
    
    def __getitem__(self, key):
        return copy.copy(record[key])

    def commit(self, key, value):
        self.record[key] = value
        with open(self.filePath, "w") as db:
            json.dump(self.record, db)


def RaftLog():
    raw = []
    index = 0

    def __init__(self, logFilePath):
        self.logFilePath = logFilePath
        if Path.exists(self.logFilePath):
            with open(self.logFilePath, "r") as log:
                self.raw = json.load(log)

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
        return copy.copy(raw[key])

    def __set_attr__(self, name, value):
        raise KeyError
    
    def appendAt(self, msg, term, index):
        raw = raw[:index]
        raw.append({"msg": msg, "term": term})

        with open(self.logFilePath, "w") as log:
            json.dump(self.raw, log)

def State():
    initialized = False
    log = None
    currentTerm = None 
    votedFor = None
    commitLength = None

    def __init__(self, node):
        Path(f"./logs_node_{node.id}").mkdir(parents=True, exist_ok=True)
        self.metadataFilePath = f"./logs_node_{node.id}/logs.txt"
        self.logFilePath = f"./logs_node_{node.id}/logs.txt"
        
        if Path.exists(self.metadataFilePath):
            with open(self.metadataFilePath, "r") as metadata:
                self.currentTerm, self.votedFor, self.commitLength = metadata.readline().split()

        log = RaftLog(self.logFilePath)

    def __set_attr__(self, name, value):
        if initialized:
            if name in ["currentTerm", "votedFor", "commitLength"]:
                with open(self.metadataFilePath, "w") as metadata:
                    metadata.write("{self.currentTerm} {self.votedFor} {self.commitLength}")
            else:
                raise AttributeError(f"State does not allow assignment to .{name} member")

def Logger():
    # node - current Node. Used to resolve path to log file
    def __init__(self, node):
        Path(f"./logs_node_{node.id}").mkdir(parents=True, exist_ok=True)
        self.file = open(f"./logs_node_{node.id}/dump.txt", "w")

    def log(self, message):
        self.file.write(message)

    def __del__(self):
        self.file.close()
