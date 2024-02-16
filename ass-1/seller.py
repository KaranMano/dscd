from __future__ import print_function
import argparse
from concurrent import futures
import json
import logging
import os
import signal
import sys
import socket
import uuid

import grpc
import market_pb2
import market_pb2_grpc
import utils

db = {} 
stub = None
isExitCalled = False
ip = "127.0.0.1"
port = "50052"
marketAddress = "localhost:50051"

def loadDB():
    global db
    if os.path.exists("seller-db.json"):
        with open("seller-db.json", "r") as dbDump:
            dbSerializable = json.load(dbDump)
            db = {
                "sellerInfo": market_pb2.SellerInfo(
                    address=dbSerializable["address"], 
                    uuid=dbSerializable["uuid"]
                )
            }
    else:
        db = {
            "sellerInfo": market_pb2.SellerInfo(address=f"{ip}:{port}", uuid=uuid.uuid4().hex)
            }
def dumpDB():
    global db
    with open("seller-db.json", "w") as dbDump:
        dbSerializable = { 
            "address": db["sellerInfo"].address,
            "uuid": db["sellerInfo"].uuid
            }
        json.dump(dbSerializable, dbDump)

def Register(args, manager):
    response = stub.Register(market_pb2.RegistrationRequest(sellerInfo=db["sellerInfo"]))
    print(market_pb2.Status.Name(response.status))
    if response.status == market_pb2.Status.FAIL:
        print("Might already be registered")
def Sell(args, manager):
    try:
        name = args[0]
        category = market_pb2.Category.Value(args[1])
        quantity = int(args[2])
        description = args[3]
        pricePerUnit = int(args[4])
    except:
        manager.notifyParseError()
        return
    itemInfo = market_pb2.ItemInfo(
        name=name,
        category=category,
        quantity=quantity,
        description=description,
        pricePerUnit=pricePerUnit
    )
    response = stub.SellItem(market_pb2.SellRequest(
                itemInfo=itemInfo,
                sellerInfo=db["sellerInfo"]
                ))
    print(market_pb2.Status.Name(response.status))
def Update(args, manager):
    try:
        itemID = int(args[0])
        quantity = int(args[1])
        pricePerUnit = int(args[2])
    except:
        manager.notifyParseError()
    response = stub.UpdateItem(market_pb2.UpdateRequest(
                itemID=itemID,
                quantity=quantity,
                pricePerUnit=pricePerUnit,
                sellerInfo=db["sellerInfo"]
                ))
    print(market_pb2.Status.Name(response.status))
def Delete(args, manager):
    try:
        itemID = int(args[0])
    except:
        manager.notifyParseError()
    response = stub.DeleteItem(market_pb2.DeleteRequest(
                itemID=itemID,
                sellerInfo=db["sellerInfo"]
                ))
    print(market_pb2.Status.Name(response.status))
def Display(args, manager):
    response = stub.DisplayItems(market_pb2.DisplayRequest(
                sellerInfo=db["sellerInfo"]
                ))
    utils.printItemList(response)
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
        TUIManager.addCommand("REGISTER", Register, "REGISTER")
        TUIManager.addCommand("SELL", Sell, "SELL <name> <category> <quantity> <description> <price-per-unit>\n Available categories: ELECTRONICS, FASHION, OTHERS")
        TUIManager.addCommand("UPDATE", Update, "UPDATE <itemID> <quantity> <price-per-unit>")
        TUIManager.addCommand("DELETE", Delete, "DELETE <itemID>")
        TUIManager.addCommand("DISPLAY", Display, "DISPLAY")
        TUIManager.addCommand("EXIT", Exit, "EXIT")
        stub = market_pb2_grpc.SellerServiceStub(channel)  
        print(f"Market IP address: {marketAddress}")  
        print("Seller portal, enter HELP for command list")
        try:
            while not isExitCalled:
                TUIManager.run()
        except KeyboardInterrupt as e:
            server.stop(None)

def sigintHandler(sig, frame):
    dumpDB()
    sys.exit(0)

if __name__ == "__main__":
    logging.basicConfig()
    signal.signal(signal.SIGINT, sigintHandler)
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--market", help="The IP address of the market")
    args = parser.parse_args()
    if args.market:
        marketAddress = args.market 
    ip = socket.gethostbyname(socket.gethostname())
    loadDB()
    run()
    dumpDB()

