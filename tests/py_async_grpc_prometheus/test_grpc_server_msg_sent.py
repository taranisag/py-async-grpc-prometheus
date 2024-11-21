import pytest

from tests.conftest import GrpcStub
from tests.py_async_grpc_prometheus.utils import get_server_metric
from tests.integration.hello_world import hello_world_pb2


@pytest.mark.asyncio
@pytest.mark.parametrize("target_count", [1, 10, 100])
async def test_grpc_server_msg_sent_with_normal(
    target_count, grpc_stub: GrpcStub
):
  responses = []
  for i in range(target_count):
    response = await grpc_stub.stub.SayHello(hello_world_pb2.HelloRequest(name=str(i)))
    responses.append(response)
  target_metric = get_server_metric("grpc_server_msg_sent", grpc_stub.prom_server_port)
  # None streaming request has no this metrics
  assert target_metric.samples == []
  assert len(responses) == target_count


@pytest.mark.asyncio
@pytest.mark.parametrize("number_of_res", [1, 10, 100])
async def test_grpc_server_msg_sent_with_unary_stream(
    number_of_res, grpc_stub: GrpcStub
):
  responses = []
  async for response in grpc_stub.stub.SayHelloUnaryStream(
          hello_world_pb2.MultipleHelloResRequest(
              name="unary stream", res=number_of_res
          )
      ):
    responses.append(response)
  target_metric = get_server_metric("grpc_server_msg_sent", grpc_stub.prom_server_port)
  assert target_metric.samples[0].value == number_of_res
  assert len(responses) == number_of_res


@pytest.mark.asyncio
@pytest.mark.parametrize("number_of_names", [1, 10, 100])
async def test_grpc_server_msg_sent_with_stream_unary(
    number_of_names, grpc_stub: GrpcStub, stream_request_generator
):
  responses = []
  responses.append(await grpc_stub.stub.SayHelloStreamUnary(
      stream_request_generator(number_of_names)
  ))
  target_metric = get_server_metric("grpc_server_msg_sent", grpc_stub.prom_server_port)
  assert target_metric.samples == []
  assert len(responses) > 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "number_of_names, number_of_res", [(1, 10), (10, 100), (100, 100)]
)
async def test_grpc_server_msg_sent_with_bidi_stream(
    number_of_names, number_of_res, grpc_stub: GrpcStub, bidi_request_generator
):
  responses = []
  async for response in grpc_stub.stub.SayHelloBidiStream(
          bidi_request_generator(number_of_names, number_of_res)
      ):
        responses.append(response)
  target_metric = get_server_metric("grpc_server_msg_sent", grpc_stub.prom_server_port)
  assert target_metric.samples[0].value == number_of_names * number_of_res
  assert len(responses) == number_of_names * number_of_res
