import market_pb2
import market_pb2_grpc

def Help(args, manager):
	manager.printHelp()
class TUIManager():
	def __init__(self) -> None:
		self.commandMap = {}
		self.help = []
		self.commandMap["HELP"] = Help
	
	def addCommand(self, name, function, help):
		self.help.append(help)
		self.commandMap[name] = function

	def run(self):
		command, *args = input().split()
		if command in self.commandMap.keys():
			self.commandMap[command](args, self)
		else:
			print("Undefined command enter HELP to get full command list")

	def printHelp(self):
		print("Command List:")
		for help in self.help:
			print("\t" + help)
		
	def notifyParseError(self):
		print("Failed while parsing args enter HELP to check command args")

def printItemList(itemList):
	for i in range(len(itemList.itemIDs)):
		print(f"Item ID: {itemList.itemIDs[i]},", end=" ")
		print(f"Price: ${itemList.itemInfos[i].pricePerUnit},", end=" ")
		print(f"Name: {itemList.itemInfos[i].name},", end=" ")
		print(f"Category: {market_pb2.Category.Name(itemList.itemInfos[i].category)},")
		print(f"Description: {itemList.itemInfos[i].description}.")
		print(f"Quantity Remaining: {itemList.itemInfos[i].quantity}")
		print(f"Seller: {itemList.sellerAddresses[i]}")
		print(f"Rating: {itemList.ratings[i]}/5")
		print("----")

class NotificationService(market_pb2_grpc.NotificationServiceServicer):
	def NotifyClient(self, request, context):
		print("#######")
		print("The Following Item has been updated:")
		print(f"Item ID: {request.itemID},", end=" ")
		print(f"Price: ${request.itemInfo.pricePerUnit},", end=" ")
		print(f"Name: {request.itemInfo.name},", end=" ")
		print(f"Category: {market_pb2.Category.Name(request.itemInfo.category)},")
		print(f"Description: {request.itemInfo.description}.")
		print(f"Quantity Remaining: {request.itemInfo.quantity}")
		print(f"Seller: {request.sellerAddress}")
		print(f"Rating: {request.rating}/5")
		print("#######")
		return market_pb2.Empty()