# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: main.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nmain.proto\",\n\x08\x43\x65ntroid\x12\n\n\x02id\x18\x01 \x01(\x05\x12\t\n\x01x\x18\x02 \x01(\x02\x12\t\n\x01y\x18\x03 \x01(\x02\"\x7f\n\x10MapperParameters\x12\x12\n\nn_reducers\x18\x01 \x01(\x05\x12\x13\n\x0brange_start\x18\x02 \x01(\x05\x12\x11\n\trange_end\x18\x03 \x01(\x05\x12\x1c\n\tcentroids\x18\x04 \x03(\x0b\x32\t.Centroid\x12\x11\n\tmapper_id\x18\x05 \x01(\x05\",\n\x0eMapperResponse\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x0e\n\x06status\x18\x02 \x01(\t\"-\n\x17GetPartitionsParameters\x12\x12\n\nreducer_id\x18\x01 \x01(\x05\"E\n\x0ePartitionEntry\x12\x0b\n\x03key\x18\x01 \x01(\x05\x12\x10\n\x08point_id\x18\x02 \x01(\x05\x12\t\n\x01x\x18\x03 \x01(\x02\x12\t\n\x01y\x18\x04 \x01(\x02\"^\n\x15GetPartitionsResponse\x12\x11\n\tmapper_id\x18\x01 \x01(\x05\x12\x0e\n\x06status\x18\x02 \x01(\t\x12\"\n\tpartition\x18\x03 \x03(\x0b\x32\x0f.PartitionEntry\"D\n\x11ReducerParameters\x12\x11\n\tn_mappers\x18\x01 \x01(\x05\x12\x1c\n\tcentroids\x18\x02 \x03(\x0b\x32\t.Centroid\"i\n\x12ReducerOutputEntry\x12\x1b\n\x13\x63urrent_centroid_id\x18\x01 \x01(\x05\x12\x1a\n\x12updated_centroid_x\x18\x02 \x01(\x02\x12\x1a\n\x12updated_centroid_y\x18\x03 \x01(\x02\"S\n\x0fReducerResponse\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x0e\n\x06status\x18\x02 \x01(\t\x12$\n\x07\x65ntries\x18\x03 \x03(\x0b\x32\x13.ReducerOutputEntry2\x83\x01\n\x06Mapper\x12\x34\n\x0cInvokeMapper\x12\x11.MapperParameters\x1a\x0f.MapperResponse\"\x00\x12\x43\n\rGetPartitions\x12\x18.GetPartitionsParameters\x1a\x16.GetPartitionsResponse\"\x00\x32\x42\n\x07Reducer\x12\x37\n\rInvokeReducer\x12\x12.ReducerParameters\x1a\x10.ReducerResponse\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'main_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_CENTROID']._serialized_start=14
  _globals['_CENTROID']._serialized_end=58
  _globals['_MAPPERPARAMETERS']._serialized_start=60
  _globals['_MAPPERPARAMETERS']._serialized_end=187
  _globals['_MAPPERRESPONSE']._serialized_start=189
  _globals['_MAPPERRESPONSE']._serialized_end=233
  _globals['_GETPARTITIONSPARAMETERS']._serialized_start=235
  _globals['_GETPARTITIONSPARAMETERS']._serialized_end=280
  _globals['_PARTITIONENTRY']._serialized_start=282
  _globals['_PARTITIONENTRY']._serialized_end=351
  _globals['_GETPARTITIONSRESPONSE']._serialized_start=353
  _globals['_GETPARTITIONSRESPONSE']._serialized_end=447
  _globals['_REDUCERPARAMETERS']._serialized_start=449
  _globals['_REDUCERPARAMETERS']._serialized_end=517
  _globals['_REDUCEROUTPUTENTRY']._serialized_start=519
  _globals['_REDUCEROUTPUTENTRY']._serialized_end=624
  _globals['_REDUCERRESPONSE']._serialized_start=626
  _globals['_REDUCERRESPONSE']._serialized_end=709
  _globals['_MAPPER']._serialized_start=712
  _globals['_MAPPER']._serialized_end=843
  _globals['_REDUCER']._serialized_start=845
  _globals['_REDUCER']._serialized_end=911
# @@protoc_insertion_point(module_scope)
