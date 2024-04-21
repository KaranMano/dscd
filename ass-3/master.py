import argparse
import sys
import time
from pprint import pprint
from pathlib import Path
import copy
import numpy as np
import logging
import grpc
import main_pb2_grpc
import main_pb2
import threading

logging.getLogger("grpc").setLevel(logging.NOTSET)
from multiprocessing import Process
from mapper import invoke_mapper
from reducer import invoke_reducer
import matplotlib.pyplot as plt

NODE_TYPE = "master"

# master params
n_mappers = None
n_reducers = None
n_centroids = None
n_iterations = None

# globals
logger = logging.getLogger(__name__)
points = []

mapper_responses = {}
reducer_responses = []

lock = threading.Lock()


def get_input():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mappers", help="Number of mappers", type=int)
    parser.add_argument("-r", "--reducers", help="Number of reducers", type=int)
    parser.add_argument("-c", "--centroids", help="Number of centroids", type=int)
    parser.add_argument("-i", "--iterations", help="Number of iterations", type=int)
    args = parser.parse_args()
    if (
        (args.mappers == None)
        or (args.reducers == None)
        or (args.centroids == None)
        or (args.iterations == None)
    ):
        print(
            "[INPUT_ERR]: number of mappers, reducers, centroids, iterations are required. Exiting..."
        )
        sys.exit(-1)

    global n_mappers, n_reducers, n_centroids, n_iterations
    n_mappers = args.mappers
    n_reducers = args.reducers
    n_centroids = args.centroids
    n_iterations = args.iterations


def setup_logging():
    Path(f"./logs_{NODE_TYPE}").mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=f"./logs_{NODE_TYPE}/dump.txt",
        filemode="w",
        format="[%(asctime)s] : %(message)s",
        datefmt="%I:%M:%S %p",
        level=logging.INFO,
    )
    logger.info(f"Initialized node: {NODE_TYPE}")


def load_points():
    with open("Data/Input/points.txt", "r") as pointEntry:
        for idx, entry in enumerate(pointEntry):
            x, y = list(map(lambda x: float(x.strip()), entry.split(",")))
            points.append([idx, x, y])


def get_input_split():
    shuffled_point_indices = []
    mapper_batch = len(points) // n_mappers
    mapper_rem = len(points) % n_mappers
    offset = 0
    for i in range(0, n_mappers):
        if mapper_rem > 0:
            shuffled_point_indices.append([offset, offset + mapper_batch])
            mapper_rem -= 1
            offset += mapper_batch + 1
        else:
            shuffled_point_indices.append([offset, offset + mapper_batch - 1])
            offset += mapper_batch
    return shuffled_point_indices


def get_randomized_centroids():
    shuffled_points = np.array(points)
    np.random.shuffle(shuffled_points)
    centroids = []
    for i in range(0, n_centroids):
        centroids.append(
            list(
                [
                    int(shuffled_points[i][0]),
                    float(shuffled_points[i][1]),
                    float(shuffled_points[i][2]),
                ]
            )
        )
    return list(centroids)


def spawn_subprocesses():
    mappers = []
    for i in range(0, n_mappers):
        mappers.append(Process(target=invoke_mapper, args=(i,)))
    for mapper_process in mappers:
        mapper_process.start()
    reducers = []
    for i in range(0, n_reducers):
        reducers.append(Process(target=invoke_reducer, args=(i,)))
    for reducer_process in reducers:
        reducer_process.start()


def call_mapper_rpc(m_id, start, end):
    global mapper_responses
    m_port = 5000 + m_id
    m_channel = grpc.insecure_channel(f"localhost:{m_port}")
    stub = main_pb2_grpc.MapperStub(m_channel)

    stub_req_obj = main_pb2.MapperParameters()
    stub_req_obj.n_reducers = n_reducers
    stub_req_obj.range_start = start
    stub_req_obj.range_end = end
    stub_req_obj.mapper_id = m_id

    for cent in centroids:
        c_id, c_x, c_y = cent
        stub_req_obj.centroids.append(main_pb2.Centroid(id=(c_id), x=(c_x), y=(c_y)))

    res = stub.InvokeMapper(stub_req_obj)
    logger.info(f"received response from mapper {res}")
    lock.acquire()
    mapper_responses[m_id] = res
    lock.release()
    return


def call_reducer_rpc(r_id):
    global reducer_responses
    r_port = 10000 + r_id
    r_channel = grpc.insecure_channel(f"localhost:{r_port}")
    stub = main_pb2_grpc.ReducerStub(r_channel)

    stub_req_obj = main_pb2.ReducerParameters()
    stub_req_obj.n_mappers = n_mappers

    for cent in centroids:
        c_id, c_x, c_y = cent
        stub_req_obj.centroids.append(main_pb2.Centroid(id=int(c_id), x=(c_x), y=(c_y)))

    res = stub.InvokeReducer(stub_req_obj)
    logger.info(f"received response from reducer {res}")
    lock.acquire()
    reducer_responses.extend(
        [entry.current_centroid_id, entry.updated_centroid_x, entry.updated_centroid_y]
        for entry in res.entries
    )
    lock.release()
    return


def create_plot(iteration, centroids):
    x_data = [p[1] for p in points]
    x_data.extend([p[1] for p in centroids])
    y_data = [p[2] for p in points]
    y_data.extend([p[2] for p in centroids])
    colors = ["#001177" for i in range(len(points))]
    colors.extend(["#771100" for i in range(n_centroids)])
    plt.scatter(x_data, y_data, s=50, c=colors, alpha=0.7)
    plt.title(f"iteration: {iteration}")
    plt.show()

def save_centroids(last_centroids):
    logger.info(f"saving final centroids: {last_centroids}")
    with open(f"Data/centroids.txt", "w") as partition_file:
        for point in last_centroids:
            _, pointx, pointy = point
            partition_file.write(f"{pointx}, {pointy}\n")


if __name__ == "__main__":
    print("Started ✅")
    get_input()
    setup_logging()
    load_points()
    split_points = get_input_split()
    centroids = get_randomized_centroids()

    logger.info(f"pts {points}")
    logger.info(f"split ranges {split_points}")
    logger.info(f"centroids {centroids}")

    spawn_subprocesses()
    time.sleep(1)
    last_centroids = centroids
    stop_iterations = True
    for iteration in range(0, n_iterations):
        logger.info(f"[ITER] executing iteration {iteration} ...")
        mapper_request_threads = []
        for i in range(n_mappers):
            m_t = threading.Thread(
                target=call_mapper_rpc, args=(i, split_points[i][0], split_points[i][1])
            )
            m_t.start()
            mapper_request_threads.append(m_t)
        for m_t in mapper_request_threads:
            res = m_t.join()
        logger.info(f"waiting for all mappers to finish ...")
        logger.info(f"[MAPPER RES] mapper responses joined {mapper_responses}")
        mapper_responses = {}
        
        reducer_request_threads = []
        for i in range(n_reducers):
            r_t = threading.Thread(target=call_reducer_rpc, args=(i,))
            r_t.start()
            reducer_request_threads.append(r_t)
        for r_t in reducer_request_threads:
            res = r_t.join()
        logger.info(f"waiting for all reducers to finish ...")
        logger.info(f"[REDUCER RES] reducer responses joined {reducer_responses}")
        # pprint(reducer_responses)
        create_plot(iteration, centroids)
        updated_centroids = reducer_responses
        reducer_responses = []
        
        # pprint(f"curr: {updated_centroids}")
        # pprint(f"last: {last_centroids}")
        for i in range(n_centroids):
            if not (
                last_centroids[i][1] - updated_centroids[i][1] < 0.001
                and last_centroids[i][2] - updated_centroids[i][2] < 0.001
            ):
                stop_iterations = False
        last_centroids = copy.copy(updated_centroids)
        
        if stop_iterations:
            logger.info(f"Convergence reached at {iteration}th loop. Stopping...")
            break
    save_centroids(last_centroids)
    exit(1)
