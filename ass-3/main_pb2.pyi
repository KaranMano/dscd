from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Centroid(_message.Message):
    __slots__ = ("id", "x", "y")
    ID_FIELD_NUMBER: _ClassVar[int]
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    id: int
    x: float
    y: float
    def __init__(self, id: _Optional[int] = ..., x: _Optional[float] = ..., y: _Optional[float] = ...) -> None: ...

class MapperParameters(_message.Message):
    __slots__ = ("n_reducers", "range_start", "range_end", "centroids", "mapper_id")
    N_REDUCERS_FIELD_NUMBER: _ClassVar[int]
    RANGE_START_FIELD_NUMBER: _ClassVar[int]
    RANGE_END_FIELD_NUMBER: _ClassVar[int]
    CENTROIDS_FIELD_NUMBER: _ClassVar[int]
    MAPPER_ID_FIELD_NUMBER: _ClassVar[int]
    n_reducers: int
    range_start: int
    range_end: int
    centroids: _containers.RepeatedCompositeFieldContainer[Centroid]
    mapper_id: int
    def __init__(self, n_reducers: _Optional[int] = ..., range_start: _Optional[int] = ..., range_end: _Optional[int] = ..., centroids: _Optional[_Iterable[_Union[Centroid, _Mapping]]] = ..., mapper_id: _Optional[int] = ...) -> None: ...

class MapperResponse(_message.Message):
    __slots__ = ("id", "status")
    ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    id: int
    status: str
    def __init__(self, id: _Optional[int] = ..., status: _Optional[str] = ...) -> None: ...

class GetPartitionsParameters(_message.Message):
    __slots__ = ("reducer_id",)
    REDUCER_ID_FIELD_NUMBER: _ClassVar[int]
    reducer_id: int
    def __init__(self, reducer_id: _Optional[int] = ...) -> None: ...

class PartitionEntry(_message.Message):
    __slots__ = ("key", "point_id", "x", "y")
    KEY_FIELD_NUMBER: _ClassVar[int]
    POINT_ID_FIELD_NUMBER: _ClassVar[int]
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    key: int
    point_id: int
    x: float
    y: float
    def __init__(self, key: _Optional[int] = ..., point_id: _Optional[int] = ..., x: _Optional[float] = ..., y: _Optional[float] = ...) -> None: ...

class GetPartitionsResponse(_message.Message):
    __slots__ = ("mapper_id", "status", "partition")
    MAPPER_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    PARTITION_FIELD_NUMBER: _ClassVar[int]
    mapper_id: int
    status: str
    partition: _containers.RepeatedCompositeFieldContainer[PartitionEntry]
    def __init__(self, mapper_id: _Optional[int] = ..., status: _Optional[str] = ..., partition: _Optional[_Iterable[_Union[PartitionEntry, _Mapping]]] = ...) -> None: ...

class ReducerParameters(_message.Message):
    __slots__ = ("n_mappers", "centroids")
    N_MAPPERS_FIELD_NUMBER: _ClassVar[int]
    CENTROIDS_FIELD_NUMBER: _ClassVar[int]
    n_mappers: int
    centroids: _containers.RepeatedCompositeFieldContainer[Centroid]
    def __init__(self, n_mappers: _Optional[int] = ..., centroids: _Optional[_Iterable[_Union[Centroid, _Mapping]]] = ...) -> None: ...

class ReducerOutputEntry(_message.Message):
    __slots__ = ("current_centroid_id", "updated_centroid_x", "updated_centroid_y")
    CURRENT_CENTROID_ID_FIELD_NUMBER: _ClassVar[int]
    UPDATED_CENTROID_X_FIELD_NUMBER: _ClassVar[int]
    UPDATED_CENTROID_Y_FIELD_NUMBER: _ClassVar[int]
    current_centroid_id: int
    updated_centroid_x: float
    updated_centroid_y: float
    def __init__(self, current_centroid_id: _Optional[int] = ..., updated_centroid_x: _Optional[float] = ..., updated_centroid_y: _Optional[float] = ...) -> None: ...

class ReducerResponse(_message.Message):
    __slots__ = ("id", "status", "entries")
    ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    id: int
    status: str
    entries: _containers.RepeatedCompositeFieldContainer[ReducerOutputEntry]
    def __init__(self, id: _Optional[int] = ..., status: _Optional[str] = ..., entries: _Optional[_Iterable[_Union[ReducerOutputEntry, _Mapping]]] = ...) -> None: ...
