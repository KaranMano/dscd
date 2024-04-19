# Assignment 02
Modified raft with leader lease for quicker, linearized reads.

### How to run
- Update `pip`
- Install `grpcio` from `pip`
- Install `grpioc-tools` from `pip`
- Use grpc command to generate stub from node.proto (`python3 -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=. ./node.proto`
)
- Run using `python3 node.py -i <node_id>` on the respective node
- Create a nodes.txt file using the given format to assign ip addresses and ports to the nodes.

