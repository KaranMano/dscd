import argparse
import sys
from pathlib import Path
import numpy as np
import logging
import grpc
logging.getLogger('grpc').setLevel(logging.NOTSET)
from multiprocessing import Process
from mapper import invoke_mapper
from reducer import invoke_reducer


NODE_TYPE = "master"

# master params
n_mappers = 5
n_reducers = 5
n_centroids = 5
n_iterations = 5

# globals
logger = logging.getLogger(__name__)
points = []


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
    for i in range(0, n_centroids + 1):
        centroids.append(list(shuffled_points[i]))
    return centroids

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

if __name__ == "__main__":
    get_input()
    setup_logging()
    load_points()
    split_points = get_input_split()
    centroids = get_randomized_centroids()

    print("pts", points, "\n")
    print("split pts", split_points, "\n")
    print("cent", centroids, "\n")

    spawn_subprocesses()