from __future__ import print_function
import grpc
import node_pb2
import node_pb2_grpc
from defs import *
from concurrent import futures

stub = None
isExitCalled = False
leaderID = 0
channel = None

def Help(args, manager):
    manager.printHelp()


class TUIManager:
    def __init__(self) -> None:
        self.commandMap = {}
        self.help = []
        self.commandMap["HELP"] = Help

    def addCommand(self, name, function, help):
        self.help.append(help)
        self.commandMap[name] = function

    def run(self):
        command, *args = input().split()
        if command.upper() in self.commandMap.keys():
            self.commandMap[command.upper()](args, self)
        else:
            print("Undefined command enter HELP to get full command list")

    def printHelp(self):
        print("Command List:")
        for help in self.help:
            print("\t" + help)

    def notifyParseError(self):
        print("Failed while parsing args enter HELP to check command args")


def Set(args, manager):
    global channel
    global stub
    global leaderID
    try:
        key, *value = args
        value = ' '.join(value)
    except:
        manager.notifyParseError()
    while True:
        try:
            response = stub.ServeClient(
                node_pb2.ServeClientArgs(request=f"SET, {key}, {value}")
            )
            if not response.success:
                leaderID = response.leaderID
                channel = grpc.insecure_channel(f"{nodes[leaderID][0]}:{nodes[leaderID][1]}")
                stub = node_pb2_grpc.ClientStub(channel)
            else:
                print(response)
                return
        except BaseException as e:
            leaderID = (leaderID + 1) % (len(nodes) - 1)

def Get(args, manager):
    global channel
    global stub
    global leaderID
    try:
        key = args[0]
    except:
        manager.notifyParseError()
    while True:
        try:
            response = stub.ServeClient(node_pb2.ServeClientArgs(request=f"GET, {key}"))
            print(response)
            if not response.success:
                leaderID = response.leaderID
                channel = grpc.insecure_channel(f"{nodes[leaderID][0]}:{nodes[leaderID][1]}")
                stub = node_pb2_grpc.ClientStub(channel)
            else:
                print(response)
                return
        except BaseException:
            leaderID = (leaderID + 1) % (len(nodes) - 1)

def Exit(args, manager):
    global isExitCalled
    isExitCalled = True

def run():
    global stub
    global isExitCalled
    global channel
    
    manager = TUIManager()
    manager.addCommand("SET", Set, "Set <key> <value>")
    manager.addCommand("GET", Get, "GET <key>")
    manager.addCommand("EXIT", Exit, "EXIT")
    print("Client portal, enter HELP for command list")
    while not isExitCalled:
        channel = grpc.insecure_channel(f"{nodes[leaderID][0]}:{nodes[leaderID][1]}")
        stub = node_pb2_grpc.ClientStub(channel)
        manager.run()
        channel.close()

# Example usage
if __name__ == "__main__":
    nodes = loadNodes()
    run()
