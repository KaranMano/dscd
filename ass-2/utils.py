import socket

def loadNodes(nodes: dict):
    with open("nodes.txt", "r") as nodeRegistry:
        next(nodeRegistry)
        for entry in nodeRegistry:
            ID, ip = entry.split()
            ID = int(ID)
            nodes[ID] = ip

def getCurrentIPAddress():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    IPAddr = s.getsockname()[0]
    s.close()
    return IPAddr