import sys
import socket
from defs import *
import logging
from pathlib import Path
import grpc
import random
import time
import node_pb2
import node_pb2_grpc
from operator import itemgetter
import asyncio
import argparse
from context import Context

# globals
logger = logging.getLogger(__name__)

def loadNodes():
    nodes = []
    with open("nodes.txt", "r") as nodeRegistry:
        next(nodeRegistry)
        for entry in nodeRegistry:
            ID, ip, port = entry.split()
            nodes.append([ip, port])
    return nodes

def getLocalIPAddress():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    IPAddr = s.getsockname()[0]
    s.close()
    return IPAddr

async def startRaft(ID, ip, port ,nodes):
    state = Context(ID, ip, port, nodes)
    server = grpc.aio.server()
    node_pb2_grpc.add_NodeServicer_to_server(NodeServicer(state), server)
    node_pb2_grpc.add_ClientServicer_to_server(ClientServicer(state), server)
    listen_addr = f"{ip}:{port}"
    server.add_insecure_port(listen_addr)
    logging.info("Starting server on %s", listen_addr)
    await server.start()
    await server.wait_for_termination()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", help="The port of the node")
    parser.add_argument("-i", "--id", help="The id of the node")
    args = parser.parse_args()
    if not (args.port and args.id):
        print("port and id needed")
        sys.exit(-1) 

    # non-raft globals init
    nodes = loadNodes()
    ID = args.id
    ip = getLocalIPAddress()
    port = args.port
    
    # logging setup
    Path(f"./logs_node_{ID}").mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=f"./logs_node_{ID}/dump.txt", filemode='w', level=logging.INFO)
    logger.info(f"Acquired address: {ID} {ip}:{port}")

    logger.info(nodes)
    
    # raft init
    asyncio.run(startRaft(ID, ip, port, nodes))
