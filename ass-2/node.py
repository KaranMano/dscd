import sys
import socket
from database import Database
from defs import State, NodeType
import logging
from pathlib import Path

# globals
nodes = {}
state = None
db = None
logger = logging.getLogger(__name__)

def loadNodes():
    with open("nodes.txt", "r") as nodeRegistry:
        next(nodeRegistry)
        for entry in nodeRegistry:
            ID, ip = entry.split()
            ID = int(ID)
            nodes[ID] = ip

def startElection():
    state.currentTerm += + 1
    state.currentRole = NodeType.CANDIDATE
    state.votedFor = state.ID
    state.votesReceived.add(state.ID)
    lastTerm = 0
    if len(state.log) > 0:
        lastTerm = state.log[len(state.log) - 1]["term"]
    #! create message msg = ("VoteRequest", currNode.id, currentTerm, log.length, lastTerm)
    for node in nodes:
        pass
        #! send rpc
    #! start election timer
    
def run():
    pass

def getIPAddress():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    IPAddr = s.getsockname()[0]
    s.close()
    return IPAddr

if __name__ == "__main__":
    # non-raft globals init
    loadNodes()
    ip = getIPAddress()
    ID, *_ = [key for key, val in nodes.items() if val == ip]
    if ID == None:
        print("Current IP address has no corresponding entry in nodes.txt")
        sys.exit(-1)
    Path(f"./logs_node_{ID}").mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=f'./logs_node_{ID}/dump.txt', filemode='w', level=logging.INFO)

    # raft init 
    state = State(ID, nodes[ID])
    db = Database(ID)

    run()
