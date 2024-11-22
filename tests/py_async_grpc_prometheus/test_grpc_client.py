import pytest

from tests.conftest import GrpcStub
from tests.py_async_grpc_prometheus.utils import get_metric
from tests.integration.hello_world import hello_world_pb2

@pytest.mark.asyncio
async def test_grpc_client(grpc_stub: GrpcStub):
    await grpc_stub.stub.SayHello(
        hello_world_pb2.HelloRequest(name="delay")
    )
    target_metric = get_metric(
        "grpc_client_handling_seconds", grpc_stub.prom_client_port
    )
    assert len(target_metric.samples) != 0
    for sample in target_metric.samples:
        if sample.name == "grpc_client_handling_seconds_bucket":
            if sample.labels["le"] == "0.005":
                found005 = True
                assert sample.value == 0.0
            if sample.labels["le"] == "+Inf":
                foundInf = True
                assert sample.value == 1.0
    assert found005
    assert foundInf

@pytest.mark.asyncio
async def test_grpc_client_unary_stream(grpc_stub: GrpcStub):
    async for response in grpc_stub.stub.SayHelloUnaryStream(
        hello_world_pb2.MultipleHelloResRequest(name="delay", res=1)
    ):
        pass
    target_metric = get_metric(
        "grpc_client_handling_seconds", grpc_stub.prom_client_port
    )
    assert len(target_metric.samples) != 0
    for sample in target_metric.samples:
        if sample.name == "grpc_client_handling_seconds_bucket":
            if sample.labels["le"] == "0.005":
                found005 = True
                assert sample.value == 0.0
            if sample.labels["le"] == "+Inf":
                foundInf = True
                assert sample.value == 1.0

    assert found005
    assert foundInf

@pytest.mark.asyncio
async def test_grpc_client_stream_unary(grpc_stub: GrpcStub):
    async def requests():
        yield hello_world_pb2.HelloRequest(name="delay")
    await grpc_stub.stub.SayHelloStreamUnary(requests())
    target_metric = get_metric(
        "grpc_client_handling_seconds", grpc_stub.prom_client_port
    )
    assert len(target_metric.samples) != 0
    for sample in target_metric.samples:
        if sample.name == "grpc_client_handling_seconds_bucket":
            if sample.labels["le"] == "0.005":
                found005 = True
                assert sample.value == 0.0
            if sample.labels["le"] == "+Inf":
                foundInf = True
                assert sample.value == 1.0

    assert found005
    assert foundInf

    # Test that non async iterables work as well
    await grpc_stub.stub.SayHelloStreamUnary([hello_world_pb2.HelloRequest(name="delay")])
