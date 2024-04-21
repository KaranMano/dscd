import os

def shuffle_sort(partitioned_batches):
    # partitioned batches is a list of
    # [key ind x y]
    # compiled from outputs of all mappers
    merged_partitions = {}
    for entry in partitioned_batches:
        closest_centroid_id = entry.key
        if merged_partitions.get(closest_centroid_id) == None:
            merged_partitions[closest_centroid_id] = [[entry.ind, entry.x, entry.y]]
        else:
            merged_partitions[closest_centroid_id].append([entry.ind, entry.x, entry.y])
    return merged_partitions

def kmeans_reduce(merged_partitions):
    reducer_output = []
    for current_centroid_id, points in merged_partitions.items():
        points_sum = [0.0, 0.0]
        for point_id, x, y in points:
            points_sum[0]+=x
            points_sum[1]+=y
        updated_centroid = [points_sum[0]/len(points), points_sum[1]/len(points)]
        reducer_output.append([current_centroid_id, updated_centroid[0], updated_centroid[1]])
    return reducer_output

def invoke_reducer(id):
    print(f"reducer-{id} invoked! PID={os.getpid()} parentPID={os.getppid()}")
    pass
