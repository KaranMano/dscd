from __future__ import print_function
import argparse
from concurrent import futures
import logging
import socket
import utils

import grpc
import market_pb2
import market_pb2_grpc

stub = None
isExitCalled = False
ip = "127.0.0.1"
port = "50053"
marketAddress = "localhost:50051"

def Search(args, manager):
    try:
        itemCategory = market_pb2.Category.Value(args[0])
        itemName = ""
        if len(args) > 1:
            itemName = args[1]
    except:
        manager.notifyParseError()
        return
    response = stub.SearchItem(market_pb2.SearchRequest(itemName=itemName, itemCategory=itemCategory))
    utils.printItemList(response)
def Buy(args, manager):
    try:
        itemID = int(args[0])
        quantity = int(args[1])
        address = f"{ip}:{port}"
    except:
        manager.notifyParseError()
        return
    response = stub.BuyItem(market_pb2.BuyRequest(itemID=itemID, quantity=quantity, address=address))
    print(market_pb2.Status.Name(response.status))
def WishList(args, manager):
    try:
        itemID = int(args[0])
        address = f"{ip}:{port}"
    except:
        manager.notifyParseError()
        return
    response = stub.AddToWishList(market_pb2.WishListRequest(itemID=itemID, address=address))
    print(market_pb2.Status.Name(response.status))
def Rate(args, manager):
    try:
        itemID = int(args[0])
        rating = int(args[1])
        address = f"{ip}:{port}"
    except:
        manager.notifyParseError()
        return
    response = stub.RateItem(market_pb2.RateRequest(itemID=itemID, rating=rating, address=address))
    print(market_pb2.Status.Name(response.status))
def Exit(args, manager):
    global isExitCalled
    isExitCalled = True

def run():
    global stub
    global isExitCalled
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    market_pb2_grpc.add_NotificationServiceServicer_to_server(utils.NotificationService(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()

    with grpc.insecure_channel(marketAddress) as channel:
        TUIManager = utils.TUIManager()
        TUIManager.addCommand("SEARCH", Search, "SEARCH <category> <name>")
        TUIManager.addCommand("BUY", Buy, "BUY <itemID> <quantity>")
        TUIManager.addCommand("WISH", WishList, "WISH <itemID>")
        TUIManager.addCommand("RATE", Rate, "RATE <itemID> <rating>")
        TUIManager.addCommand("EXIT", Exit, "EXIT")
        stub = market_pb2_grpc.BuyerServiceStub(channel)    
        print(f"Market IP address: {marketAddress}")
        print("Buyer portal, enter HELP for command list")
        try:
            while not isExitCalled:
                TUIManager.run()
        except KeyboardInterrupt as e:
            server.stop(None)

    server.stop(None)

if __name__ == "__main__":
    logging.basicConfig()
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--market", help="The IP address of the market")
    args = parser.parse_args()
    if args.market:
        marketAddress = args.market 
    ip = socket.gethostbyname(socket.gethostname())
    run()
    
        
