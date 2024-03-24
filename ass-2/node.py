import sys
import socket
from defs import *

# globals
nodes = []
currNode = None
state = None
db = None
logger = None

def loadNodes():
    with open("nodes.txt", "r") as nodeRegistry:
        next(nodeRegistry)
        for entry in nodeRegistry:
            nodes.append(Node(*entry.split()))

def run():
    pass

# non-raft global init
if __name__ == "__main__":
    loadNodes()
    currID, *_ = nodes(lambda node: node.ip == socket.gethostbyname("localhost"), nodes)
    if currID == None:
        print("Current IP address has no corresponding entry in nodes.txt")
        sys.exit(-1)
    state = State(currNode)
    db = DataBase(currNode)
    logger = Logger(currNode)
    run()
