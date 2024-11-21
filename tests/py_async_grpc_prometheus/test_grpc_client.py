import pytest

from tests.conftest import GrpcStub
from tests.py_async_grpc_prometheus.utils import get_server_metric
from tests.integration.hello_world import hello_world_pb2

@pytest.mark.asyncio
async def test_grpc_client(grpc_stub: GrpcStub):
    await grpc_stub.stub.SayHello(
        hello_world_pb2.HelloRequest(name="delay")
    )
    target_metric = get_server_metric(
        "grpc_client_handling_seconds", grpc_stub.prom_client_port
    )
    for sample in target_metric.samples:
        if sample.name == "grpc_client_handling_seconds_bucket":
            if sample.labels["le"] == ".005":
                assert sample.value == 0.0
            if sample.labels["le"] == "+Inf":
                assert sample.value == 1.0
