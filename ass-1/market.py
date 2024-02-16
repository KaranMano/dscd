from concurrent import futures
import logging
import os
import json
import signal
import sys

import grpc
import market_pb2
import market_pb2_grpc

db = {}

class Item():
    def __init__(self, itemInfo = None, sellerInfo = None, intializeLater = False) -> None:
        if intializeLater:
            return
        if itemInfo == None:
            raise Exception
        self.name = itemInfo.name
        self.category = itemInfo.category
        self.quantity = itemInfo.quantity
        self.description = itemInfo.description
        self.pricePerUnit = itemInfo.pricePerUnit
        self.raters = 0
        self.rating = 0.0
        self.sellerInfo = sellerInfo
        self.wishListers = []
        
    def getItemInfo(self):
        itemInfo = market_pb2.ItemInfo()
        itemInfo.name = self.name
        itemInfo.category = self.category
        itemInfo.quantity = self.quantity
        itemInfo.description = self.description
        itemInfo.pricePerUnit = self.pricePerUnit
        return itemInfo

    def toJSON(self):
        return {
            "name": self.name,
            "category": self.category,
            "quantity": self.quantity,
            "description": self.description,
            "pricePerUnit": self.pricePerUnit,
            "raters": self.raters,
            "rating": self.rating,
            "address": self.sellerInfo.address,
            "uuid": self.sellerInfo.uuid,
            "wishListers": self.wishListers
        }
    
    def fromJSON(self, obj):
        self.name = obj["name"]
        self.category = obj["category"]
        self.quantity = obj["quantity"]
        self.description = obj["description"]
        self.pricePerUnit = obj["pricePerUnit"]
        self.raters = obj["raters"]
        self.rating = obj["rating"]
        self.sellerInfo = market_pb2.SellerInfo()
        self.sellerInfo.address = obj["address"]
        self.sellerInfo.uuid = obj["uuid"]
        self.wishListers = obj["wishListers"]

def authenticateSeller(sellerInfo):
    address = sellerInfo.address
    uuid = sellerInfo.uuid
    return address in db["sellers"].keys() \
        and uuid == db["sellers"][address]

class SellerService(market_pb2_grpc.SellerServiceServicer): 
    def Register (self, request, context):
        print(f"Seller join request from {request.sellerInfo.address}[ip:port], uuid = {request.sellerInfo.uuid}")
        if  not request.sellerInfo.address in db["sellers"].keys():
            db["sellers"][request.sellerInfo.address] = request.sellerInfo.uuid
            return market_pb2.StatusResponse(status=market_pb2.Status.SUCCESS)
        return market_pb2.StatusResponse(status=market_pb2.Status.FAIL)
    
    def SellItem (self, request, context):
        print(f"Sell Item request from {request.sellerInfo.address}")
        if not authenticateSeller(request.sellerInfo) \
            or request.itemInfo.category == market_pb2.Category.ANY:
            return market_pb2.StatusResponse(status=market_pb2.Status.FAIL)
        db["items"].append(Item(request.itemInfo, request.sellerInfo))
        return market_pb2.StatusResponse(status=market_pb2.Status.SUCCESS)

    def UpdateItem (self, request, context):
        print(f"Update Item {request.itemID}[id] request from {request.sellerInfo.address}")
        if not authenticateSeller(request.sellerInfo) \
            or request.itemID < 0 or request.itemID >= len(db["items"]):
            return market_pb2.StatusResponse(status=market_pb2.Status.FAIL)
        item = db["items"][request.itemID]
        # does the editor own the item?
        if item.sellerInfo.address != request.sellerInfo.address \
            and item.sellerInfo.uuid != request.sellerInfo.uuid:
            return market_pb2.StatusResponse(status=market_pb2.Status.FAIL)
        item.pricePerUnit = request.pricePerUnit #! notify buyer
        item.quantity = request.quantity
        for wishLister in item.wishListers:
            with grpc.insecure_channel(wishLister) as channel:
                stub = market_pb2_grpc.NotificationServiceStub(channel)    
                stub.NotifyClient(market_pb2.UpdateNotification(
                    itemID=request.itemID, 
                    itemInfo=item.getItemInfo(), 
                    rating=item.rating, 
                    sellerAddress=item.sellerInfo.address
                    ))
        return market_pb2.StatusResponse(status=market_pb2.Status.SUCCESS)
        
    def DeleteItem (self, request, context):
        print(f"Delete Item {request.itemID}[id] request from {request.sellerInfo.address}")
        if not authenticateSeller(request.sellerInfo) \
            or request.itemID < 0 or request.itemID >= len(db["items"]):
            return market_pb2.StatusResponse(status=market_pb2.Status.FAIL)
        item = db["items"][request.itemID]
        # does the editor own the item?
        if item.sellerInfo.address != request.sellerInfo.address \
            and item.sellerInfo.uuid != request.sellerInfo.uuid:
            return market_pb2.StatusResponse(status=market_pb2.Status.FAIL)
        del db["items"][request.itemID]
        return market_pb2.StatusResponse(status=market_pb2.Status.SUCCESS)

    def DisplayItems (self, request, context):
        print(f"Display Items request from {request.sellerInfo.address}")
        if not authenticateSeller(request.sellerInfo):
            return market_pb2.StatusResponse(status=market_pb2.Status.FAIL)
        response = market_pb2.ItemList()
        for itemID, item in enumerate(db["items"]):
            if item.sellerInfo.address == request.sellerInfo.address \
                and item.sellerInfo.uuid == request.sellerInfo.uuid:
                response.itemIDs.append(itemID)
                itemInfo = response.itemInfos.add()
                itemInfo.name = item.getItemInfo().name
                itemInfo.category = item.getItemInfo().category
                itemInfo.quantity = item.getItemInfo().quantity
                itemInfo.description = item.getItemInfo().description
                itemInfo.pricePerUnit = item.getItemInfo().pricePerUnit
                response.sellerAddresses.append(request.sellerInfo.address)
                response.ratings.append(item.rating)
        return response

class BuyerService(market_pb2_grpc.BuyerServiceServicer):
    def SearchItem (self, request, context):
        print(f"Search request for Item name: {request.itemName}, Category: {market_pb2.Category.Name(request.itemCategory)}.")
        response = market_pb2.ItemList()
        for itemID, item in enumerate(db["items"]):
            if  item.name.lower().startswith(request.itemName.lower())  \
                and (request.itemCategory == market_pb2.Category.ANY or item.category == request.itemCategory):
                response.itemIDs.append(itemID)
                itemInfo = response.itemInfos.add()
                itemInfo.name = item.getItemInfo().name
                itemInfo.category = item.getItemInfo().category
                itemInfo.quantity = item.getItemInfo().quantity
                itemInfo.description = item.getItemInfo().description
                itemInfo.pricePerUnit = item.getItemInfo().pricePerUnit
                response.sellerAddresses.append(item.sellerInfo.address)
                response.ratings.append(item.rating)
        return response
    def BuyItem (self, request, context):
        print(f"Buy request {request.quantity}[quantity] of item {request.itemID}[item id], from {request.address}[buyer address]")
        if request.itemID < 0 or request.itemID >= len(db["items"]) \
            or db["items"][request.itemID].quantity < request.quantity:
            return market_pb2.StatusResponse(status=market_pb2.Status.FAIL)
        item = db["items"][request.itemID]
        item.quantity -= request.quantity #! notify seller
        with grpc.insecure_channel(item.sellerInfo.address) as channel:
            stub = market_pb2_grpc.NotificationServiceStub(channel)    
            stub.NotifyClient(market_pb2.UpdateNotification(
                itemID=request.itemID, 
                itemInfo=item.getItemInfo(), 
                rating=item.rating, 
                sellerAddress=item.sellerInfo.address
                ))
        return market_pb2.StatusResponse(status=market_pb2.Status.SUCCESS)

    def AddToWishList (self, request, context):
        print(f"Wishlist request of item {request.itemID}[item id], from {request.address}")
        if request.itemID < 0 or request.itemID >= len(db["items"]):
            return market_pb2.StatusResponse(status=market_pb2.Status.FAIL)
        item = db["items"][request.itemID]
        if not request.address in item.wishListers:
            item.wishListers.append(request.address)
        return market_pb2.StatusResponse(status=market_pb2.Status.SUCCESS)

    def RateItem (self, request, context): #! should there be a notification for this?
        print(f"{request.address} rated item {request.itemID}[item id] with {request.rating} stars")
        if request.rating > 5 or request.rating < 0 \
            or request.itemID < 0 or request.itemID >= len(db["items"]):
            return market_pb2.StatusResponse(status=market_pb2.Status.FAIL)
        item = db["items"][request.itemID]
        item.rating = ((item.rating * float(item.raters)) + float(request.rating)) / (item.raters + 1)
        item.raters += 1
        return market_pb2.StatusResponse(status=market_pb2.Status.SUCCESS)

def loadDB():
    global db
    if os.path.exists("db.json"):
        with open("db.json", "r") as dbDump:
            dbSerializable = json.load(dbDump)
            items = []
            for item in dbSerializable["items"]:
                items.append(Item(intializeLater=True))
                items[-1].fromJSON(item)
            db = {
                "sellers": dbSerializable["sellers"],
                "items": items
            }
    else:
        db = {
            "sellers": {}, # dict of seller address -> uuid 
            "items": []
        }

def dumpDB():
    global db
    with open('db.json', "w") as dbDump:
        dbSerializable = {
            "sellers": db["sellers"],
            "items": [item.toJSON() for item in db["items"]]
        }
        json.dump(dbSerializable, dbDump)

def serve():
    port = "50051"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    market_pb2_grpc.add_SellerServiceServicer_to_server(SellerService(), server)
    market_pb2_grpc.add_BuyerServiceServicer_to_server(BuyerService(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()

def  sigintHandler(sig, frame):
    dumpDB()
    sys.exit(0)

if __name__ == "__main__":
    logging.basicConfig()
    signal.signal(signal.SIGINT, sigintHandler)
    loadDB()
    serve()
