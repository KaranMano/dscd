import sys
from pathlib import Path
import logging

from database import Database
from raftnode import RaftNode, NodeState
from utils import *

# globals
nodes = {}
currentNode: RaftNode = None
db: Database = None

logger = logging.getLogger(__name__)


def run():
    pass


if __name__ == "__main__":
    # initializing non-raft globals
    loadNodes(nodes)
    currentIP = getCurrentIPAddress()
    CURRENT_NODE_ID, *_ = [key for key, val in nodes.items() if val == currentIP]
    if CURRENT_NODE_ID == None:
        print("Current IP address has no corresponding entry in nodes.txt")
        sys.exit(-1)
    Path(f"./logs/logs_node_{CURRENT_NODE_ID}").mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=f"./logs/logs_node_{CURRENT_NODE_ID}/dump.txt", 
        filemode="w", 
        level=logging.INFO
    )

    # intializing raft dependencies
    currentNode = RaftNode(CURRENT_NODE_ID, nodes[CURRENT_NODE_ID])
    db = Database(CURRENT_NODE_ID)


    run()
