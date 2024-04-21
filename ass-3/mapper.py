import os
from pprint import pprint
from pathlib import Path

NODE_TYPE = "mapper"
mapper_id = None

points = []
n_reducers = None
centroids = None


def load_input_points(split_range):
    points = []
    with open("Data/Input/points.txt", "r") as pointEntry:
        for idx, entry in enumerate(pointEntry):
            if idx >= split_range[0] and idx <= split_range[1]:
                x, y = list(map(lambda x: float(x.strip()), entry.split(",")))
                points.append([idx, x, y])
    return points


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

def map_batch(
    split_range=[7, 12],
    centroids_list=[
        [29.0, 9.3, 1.9],
        [15.0, 0.9, 9.6],
        [30.0, 8.6, 2.6],
        [28.0, 10.5, -0.1],
        [18.0, 0.7, 9.9],
        [12.0, 9.7, 0.8],
    ],
    num_reducers=4,
    m_id=1
):
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
    if Path(f"Data/Mappers/M{mapper_id}").exists():
        pass
    else:                
        os.mkdir(f"Data/Mappers/M{mapper_id}") 
    for idx, partition in enumerate(partitions):
        if partition != 0:
            key, values = partition
            with open(f"Data/Mappers/M{mapper_id}/p_{idx}.txt", "w") as partition_file:
                for value in values:
                    partition_file.write(f"{key}, {int(value[0])}, {value[1]}, {value[2]}\n")
        else:
            with open(f"Data/Mappers/M{mapper_id}/p_{idx}.txt", "w") as partition_file:
                partition_file.close()


def partition_batch(mapped_batch):
    points_per_centroid = {}
    for entry in mapped_batch:
        key, value = entry
        if points_per_centroid.get(key) == None:
            points_per_centroid[key] = [value]
        else:
            points_per_centroid[key].append(value)

    partitions = [0 for x in range(n_reducers)]
    for ind, [key, value] in enumerate(points_per_centroid.items()):
        if partitions[ind % n_reducers] == 0:
            partitions[ind % n_reducers] = [key, value]
        else:
            partitions[ind % n_reducers].append([key, value])
    # pprint(partitions)
    return partitions

def invoke_mapper(id):
    print(f"mapper-{id} invoked! PID={os.getpid()} parentPID={os.getppid()}")
    pass

if __name__ == "__main__":
    mapped_batch = map_batch()
    partitioned_batch = partition_batch(mapped_batch)
    save_to_partition_file(partitioned_batch)

