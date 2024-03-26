import grpc
import client_pb2
import client_pb2_grpc
import random
import time

class RaftClient:
    def __init__(self, node_addresses):
        self.node_addresses = node_addresses
        self.leader_address = None
        self.raft_stubs = {addr: client_pb2_grpc.RaftStub(grpc.insecure_channel(addr)) for addr in node_addresses}

    def find_leader(self):
        for addr, stub in self.raft_stubs.items():
            try:
                response = stub.ServeClient(client_pb2.ServeClientArgs(Request="GET leader"))
                if response.Success:
                    self.leader_address = addr
                    return stub
            except grpc.RpcError:
                continue
        raise Exception("Leader not found")

    def send_request(self, request):
        retries = 3
        for _ in range(retries):
            try:
                if not self.leader_address:
                    self.find_leader()
                response = self.raft_stubs[self.leader_address].ServeClient(client_pb2.ServeClientArgs(Request=request))
                if response.Success:
                    return response.Data
                else:
                    # Update leader information if the request was not successful
                    self.leader_address = response.LeaderID if response.LeaderID else None
            except grpc.RpcError:
                self.leader_address = None  # Reset leader address on network error
        raise Exception("Request failed after retries")

    def set(self, key, value):
        return self.send_request(f"SET {key} {value}")

    def get(self, key):
        return self.send_request(f"GET {key}")

# Example usage
if __name__ == "__main__":
    node_addresses = ["localhost:5000", "localhost:5001", "localhost:5002"]  # Example node addresses
    client = RaftClient(node_addresses)
    
    # Example SET and GET requests
    print(client.set("myKey", "myValue"))
    print(client.get("myKey"))
