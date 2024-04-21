# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import main_pb2 as main__pb2


class MapperStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.InvokeMapper = channel.unary_unary(
                '/Mapper/InvokeMapper',
                request_serializer=main__pb2.MapperParameters.SerializeToString,
                response_deserializer=main__pb2.MapperResponse.FromString,
                )
        self.GetPartitions = channel.unary_unary(
                '/Mapper/GetPartitions',
                request_serializer=main__pb2.GetPartitionsParameters.SerializeToString,
                response_deserializer=main__pb2.GetPartitionsResponse.FromString,
                )


class MapperServicer(object):
    """Missing associated documentation comment in .proto file."""

    def InvokeMapper(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetPartitions(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_MapperServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'InvokeMapper': grpc.unary_unary_rpc_method_handler(
                    servicer.InvokeMapper,
                    request_deserializer=main__pb2.MapperParameters.FromString,
                    response_serializer=main__pb2.MapperResponse.SerializeToString,
            ),
            'GetPartitions': grpc.unary_unary_rpc_method_handler(
                    servicer.GetPartitions,
                    request_deserializer=main__pb2.GetPartitionsParameters.FromString,
                    response_serializer=main__pb2.GetPartitionsResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'Mapper', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Mapper(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def InvokeMapper(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Mapper/InvokeMapper',
            main__pb2.MapperParameters.SerializeToString,
            main__pb2.MapperResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetPartitions(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Mapper/GetPartitions',
            main__pb2.GetPartitionsParameters.SerializeToString,
            main__pb2.GetPartitionsResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class ReducerStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.InvokeReducer = channel.unary_unary(
                '/Reducer/InvokeReducer',
                request_serializer=main__pb2.ReducerParameters.SerializeToString,
                response_deserializer=main__pb2.ReducerResponse.FromString,
                )


class ReducerServicer(object):
    """Missing associated documentation comment in .proto file."""

    def InvokeReducer(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ReducerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'InvokeReducer': grpc.unary_unary_rpc_method_handler(
                    servicer.InvokeReducer,
                    request_deserializer=main__pb2.ReducerParameters.FromString,
                    response_serializer=main__pb2.ReducerResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'Reducer', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Reducer(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def InvokeReducer(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Reducer/InvokeReducer',
            main__pb2.ReducerParameters.SerializeToString,
            main__pb2.ReducerResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
