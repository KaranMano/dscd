import os
from pprint import pprint
from pathlib import Path
import logging
import grpc
import traceback

logging.getLogger("grpc").setLevel(logging.NOTSET)
import main_pb2_grpc
import main_pb2
from concurrent import futures


NODE_TYPE = "mapper"
mapper_id = None
n_reducers = None

# globals
logger = logging.getLogger(__name__)

points = []
n_reducers = None
centroids = None


def setup_logging():
    Path(f"./logs_{NODE_TYPE}").mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=f"./logs_{NODE_TYPE}/dump_M{mapper_id}.txt",
        filemode="w",
        format="[%(asctime)s] : %(message)s",
        datefmt="%I:%M:%S %p",
        level=logging.INFO,
    )
    logger.info(f"Initialized node: {NODE_TYPE}")


def load_input_points(split_range):
    points = []
    with open("Data/Input/points.txt", "r") as pointEntry:
        for idx, entry in enumerate(pointEntry):
            if idx >= split_range[0] and idx <= split_range[1]:
                x, y = list(map(lambda x: float(x.strip()), entry.split(",")))
                points.append([idx, x, y])
    return points


def load_partitions(m_id, r_id):
    partition = []
    with open(f"Data/Mappers/M{m_id}/p_{r_id}.txt", "r") as partitionEntry:
        for entry in partitionEntry:
            key, ind, x, y = list(map(lambda x: float(x.strip()), entry.split(",")))
            partition.append([key, ind, x, y])
    return partition


def point_distance(point, centroid):
    return (
        (point[0] - centroid[0]) * (point[0] - centroid[0])
        + (point[1] - centroid[1]) * (point[1] - centroid[1])
    ) ** 0.5


def map_point(point):
    nearest_centroid = 0
    for ind, centroid in enumerate(centroids):
        if point_distance(point, centroid) < point_distance(
            point, centroids[nearest_centroid]
        ):
            nearest_centroid = ind
    return [nearest_centroid, point]


def map_batch(split_range, centroids_list, num_reducers, m_id):
    global n_reducers
    global centroids
    global mapper_id
    mapper_id = m_id
    n_reducers = num_reducers
    centroids = centroids_list

    points = load_input_points(split_range)
    processed = []
    for point in points:
        mapped_point = map_point(point)
        processed.append(mapped_point)
    return processed


def save_to_partition_file(partitions):
    logger.info(f"partitions: {partitions}")
    if Path(f"Data/Mappers/M{mapper_id}").exists():
        pass
    else:
        os.mkdir(f"Data/Mappers/M{mapper_id}")

    for i in range(n_reducers):
        with open(f"Data/Mappers/M{mapper_id}/p_{i}.txt", "w") as partition_file:
            partition_file.close()
            
    for partition_id, values in partitions.items():
        with open(f"Data/Mappers/M{mapper_id}/p_{partition_id}.txt", "w") as partition_file:
            logger.info(f"part entry: {values}")
            for entry in values:
                centroid, ind, pointx, pointy = entry
                partition_file.write(f"{centroid}, {int(ind)}, {pointx}, {pointy}\n")


def partition_batch(mapped_batch):
    points_per_centroid = {}
    for entry in mapped_batch:
        key, value = entry
        if points_per_centroid.get(key) == None:
            points_per_centroid[key] = [value]
        else:
            points_per_centroid[key].append(value)

    # partitions = [0 for x in range(n_reducers)]
    partitions = {}
    for centroid, points in points_per_centroid.items():
        if not (partitions.get(centroid % n_reducers)):
            partitions[centroid % n_reducers] = [
                [centroid, point[0], point[1], point[2]] for point in points
            ]
        else:
            partitions[centroid % n_reducers].extend(
                [[centroid, point[0], point[1], point[2]] for point in points]
            )

        # if partitions[ind % n_reducers] == 0:
        #     partitions[ind % n_reducers] = [[centroid, points]]
        # else:
        #     partitions[ind % n_reducers].append([centroid, points])
    return partitions


def mapper_serve(m_id):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    main_pb2_grpc.add_MapperServicer_to_server(MapperServicer(), server)
    m_port = 5000 + m_id
    server.add_insecure_port(f"localhost:{m_port}")
    logger.info(f"PORT: {m_port}")
    server.start()
    server.wait_for_termination()


def invoke_mapper(id):
    global mapper_id
    mapper_id = id
    setup_logging()
    logger.info(f"mapper-{id} invoked! PID={os.getpid()} parentPID={os.getppid()}")
    mapper_serve(mapper_id)
    pass


class MapperServicer(main_pb2_grpc.MapperServicer):
    def InvokeMapper(self, request, context):
        try:
            logger.info(request)
            global n_reducers
            n_reducers = request.n_reducers
            _centroids = [[cent.id, cent.x, cent.y] for cent in request.centroids]
            mapped_batch = map_batch(
                [request.range_start, request.range_end],
                _centroids,
                request.n_reducers,
                request.mapper_id,
            )
            partitioned_batch = partition_batch(mapped_batch)
            save_to_partition_file(partitioned_batch)
            return main_pb2.MapperResponse(id=request.mapper_id, status="OK")
        except BaseException as e:
            logger.info(traceback.print_exc(e))
            return main_pb2.MapperResponse(id=request.mapper_id, status="FAILED")

    def GetPartitions(self, request, context):
        try:
            logger.info(request)
            stub_res_obj = main_pb2.GetPartitionsResponse()
            stub_res_obj.mapper_id = mapper_id
            stub_res_obj.status = "OK"
            for partition in load_partitions(mapper_id, request.reducer_id):
                stub_res_obj.partition.append(
                    main_pb2.PartitionEntry(
                        key=int(partition[0]),
                        point_id=int(partition[1]),
                        x=float(partition[2]),
                        y=float(partition[3]),
                    )
                )
            return stub_res_obj
        except BaseException as e:
            logger.info(traceback.print_exc(e))
            return main_pb2.GetPartitionsResponse(mapper_id=mapper_id, status="FAILED")
