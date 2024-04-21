import os
import traceback
from pathlib import Path
import logging
import grpc
import threading
logging.getLogger('grpc').setLevel(logging.NOTSET)
import main_pb2_grpc
import main_pb2
from concurrent import futures

NODE_TYPE = "reducer"
reducer_id = None
n_mappers = None

# globals
logger = logging.getLogger(__name__)
lock = threading.Lock()

def setup_logging():
    Path(f"./logs_{NODE_TYPE}").mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=f"./logs_{NODE_TYPE}/dump_R{reducer_id}.txt",
        filemode="w",
        format="[%(asctime)s] : %(message)s",
        datefmt="%I:%M:%S %p",
        level=logging.INFO,
    )
    logger.info(f"Initialized node: {NODE_TYPE}")

def shuffle_sort(partitioned_batches):
    # partitioned batches is a list of
    # [key ind x y]
    # compiled from outputs of all mappers
    merged_partitions = {}
    for entry in partitioned_batches:
        closest_centroid_id = entry.key
        if merged_partitions.get(closest_centroid_id) == None:
            merged_partitions[closest_centroid_id] = [[entry.point_id, entry.x, entry.y]]
        else:
            merged_partitions[closest_centroid_id].append([entry.point_id, entry.x, entry.y])
    return merged_partitions

def kmeans_reduce(merged_partitions):
    reducer_output = []
    logger.info("sorted partitions:")
    logger.info(merged_partitions)
    for current_centroid_id, points in merged_partitions.items():
        points_sum = [0.0, 0.0]
        for point_id, x, y in points:
            points_sum[0]+=x
            points_sum[1]+=y
        updated_centroid = [points_sum[0]/len(points), points_sum[1]/len(points)]
        reducer_output.append([current_centroid_id, updated_centroid[0], updated_centroid[1]])
    return reducer_output

def save_to_output_file(reducer_output, stub_entries):
    with open(f"Data/Reducers/R_{reducer_id}.txt", "w") as output_file:
        for current_c_id, updated_x, updated_y in reducer_output:
            stub_entries.append(main_pb2.ReducerOutputEntry(current_centroid_id=int(current_c_id), updated_centroid_x=updated_x, updated_centroid_y=updated_y))
            output_file.write(f"{int(current_c_id)}, {updated_x}, {updated_y}\n")

def reducer_serve(r_id):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    main_pb2_grpc.add_ReducerServicer_to_server(ReducerServicer(), server)
    r_port = 10000 + r_id
    server.add_insecure_port(f"localhost:{r_port}")
    logger.info(f"PORT: {r_port}")
    server.start()
    server.wait_for_termination()

def invoke_reducer(id):
    global reducer_id
    reducer_id = id
    setup_logging()
    logger.info(f"reducer-{id} invoked! PID={os.getpid()} parentPID={os.getppid()}")
    reducer_serve(id)
    pass

def call_getpartition_rpc(m_id, rm_responses):
    r_port = 5000 + m_id
    r_channel = grpc.insecure_channel(f'localhost:{r_port}')
    stub = main_pb2_grpc.MapperStub(r_channel)
    res = stub.GetPartitions(main_pb2.GetPartitionsParameters(reducer_id=reducer_id))
    logger.info(res)
    lock.acquire()
    rm_responses.extend(res.partition)
    lock.release()
    return

class ReducerServicer(main_pb2_grpc.ReducerServicer):
    def InvokeReducer(self, request, context):
        try:
            logger.info(request)
            global n_mappers
            n_mappers = request.n_mappers
            # partitioned_batches = get_partitioned_batches()
            
            request_threads = []
            rm_responses = []
            for i in range(n_mappers):
                r_t = threading.Thread(target=call_getpartition_rpc, args=(i, rm_responses))
                r_t.start()
                request_threads.append(r_t)
            for r_t in request_threads:
                res = r_t.join()
            logger.info(rm_responses)
            
            merged_partitions = shuffle_sort(rm_responses)
            reducer_output = kmeans_reduce(merged_partitions)
            logger.info(f"reducer output: {reducer_output}")
            stub_res_obj = main_pb2.ReducerResponse();
            stub_res_obj.id = reducer_id
            stub_res_obj.status = "OK"
            save_to_output_file(reducer_output, stub_res_obj.entries)
            return stub_res_obj
        except BaseException as e:
            logger.info(traceback.print_exc(e))
            return main_pb2.ReducerResponse(id=reducer_id, status="FAILED")