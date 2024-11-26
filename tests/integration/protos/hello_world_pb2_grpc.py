# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from tests.integration.protos import hello_world_pb2 as tests_dot_integration_dot_protos_dot_hello__world__pb2


class GreeterStub(object):
    """The greeting service definition.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.SayHello = channel.unary_unary(
                '/Greeter/SayHello',
                request_serializer=tests_dot_integration_dot_protos_dot_hello__world__pb2.HelloRequest.SerializeToString,
                response_deserializer=tests_dot_integration_dot_protos_dot_hello__world__pb2.HelloReply.FromString,
                )
        self.SayHelloUnaryStream = channel.unary_stream(
                '/Greeter/SayHelloUnaryStream',
                request_serializer=tests_dot_integration_dot_protos_dot_hello__world__pb2.MultipleHelloResRequest.SerializeToString,
                response_deserializer=tests_dot_integration_dot_protos_dot_hello__world__pb2.HelloReply.FromString,
                )
        self.SayHelloStreamUnary = channel.stream_unary(
                '/Greeter/SayHelloStreamUnary',
                request_serializer=tests_dot_integration_dot_protos_dot_hello__world__pb2.HelloRequest.SerializeToString,
                response_deserializer=tests_dot_integration_dot_protos_dot_hello__world__pb2.HelloReply.FromString,
                )
        self.SayHelloBidiStream = channel.stream_stream(
                '/Greeter/SayHelloBidiStream',
                request_serializer=tests_dot_integration_dot_protos_dot_hello__world__pb2.MultipleHelloResRequest.SerializeToString,
                response_deserializer=tests_dot_integration_dot_protos_dot_hello__world__pb2.HelloReply.FromString,
                )


class GreeterServicer(object):
    """The greeting service definition.
    """

    def SayHello(self, request, context):
        """Sends a greeting.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SayHelloUnaryStream(self, request, context):
        """Sends one greeting, get multiple response.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SayHelloStreamUnary(self, request_iterator, context):
        """Send multiple greetings, get one response.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SayHelloBidiStream(self, request_iterator, context):
        """Send multiple greetings, get multiple response.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_GreeterServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'SayHello': grpc.unary_unary_rpc_method_handler(
                    servicer.SayHello,
                    request_deserializer=tests_dot_integration_dot_protos_dot_hello__world__pb2.HelloRequest.FromString,
                    response_serializer=tests_dot_integration_dot_protos_dot_hello__world__pb2.HelloReply.SerializeToString,
            ),
            'SayHelloUnaryStream': grpc.unary_stream_rpc_method_handler(
                    servicer.SayHelloUnaryStream,
                    request_deserializer=tests_dot_integration_dot_protos_dot_hello__world__pb2.MultipleHelloResRequest.FromString,
                    response_serializer=tests_dot_integration_dot_protos_dot_hello__world__pb2.HelloReply.SerializeToString,
            ),
            'SayHelloStreamUnary': grpc.stream_unary_rpc_method_handler(
                    servicer.SayHelloStreamUnary,
                    request_deserializer=tests_dot_integration_dot_protos_dot_hello__world__pb2.HelloRequest.FromString,
                    response_serializer=tests_dot_integration_dot_protos_dot_hello__world__pb2.HelloReply.SerializeToString,
            ),
            'SayHelloBidiStream': grpc.stream_stream_rpc_method_handler(
                    servicer.SayHelloBidiStream,
                    request_deserializer=tests_dot_integration_dot_protos_dot_hello__world__pb2.MultipleHelloResRequest.FromString,
                    response_serializer=tests_dot_integration_dot_protos_dot_hello__world__pb2.HelloReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'Greeter', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Greeter(object):
    """The greeting service definition.
    """

    @staticmethod
    def SayHello(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Greeter/SayHello',
            tests_dot_integration_dot_protos_dot_hello__world__pb2.HelloRequest.SerializeToString,
            tests_dot_integration_dot_protos_dot_hello__world__pb2.HelloReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SayHelloUnaryStream(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/Greeter/SayHelloUnaryStream',
            tests_dot_integration_dot_protos_dot_hello__world__pb2.MultipleHelloResRequest.SerializeToString,
            tests_dot_integration_dot_protos_dot_hello__world__pb2.HelloReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SayHelloStreamUnary(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_unary(request_iterator, target, '/Greeter/SayHelloStreamUnary',
            tests_dot_integration_dot_protos_dot_hello__world__pb2.HelloRequest.SerializeToString,
            tests_dot_integration_dot_protos_dot_hello__world__pb2.HelloReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SayHelloBidiStream(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_stream(request_iterator, target, '/Greeter/SayHelloBidiStream',
            tests_dot_integration_dot_protos_dot_hello__world__pb2.MultipleHelloResRequest.SerializeToString,
            tests_dot_integration_dot_protos_dot_hello__world__pb2.HelloReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
