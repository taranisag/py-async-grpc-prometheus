import pytest

from tests.py_grpc_prometheus.utils import get_server_metric
from tests.integration.hello_world import hello_world_pb2


@pytest.mark.asyncio
@pytest.mark.parametrize("target_count", [1, 10, 100])
async def test_grpc_server_msg_sent_with_normal(
    target_count, grpc_server, grpc_stub
):  # pylint: disable=unused-argument
  responses = []
  for i in range(target_count):
    response = await grpc_stub.SayHello(hello_world_pb2.HelloRequest(name=str(i)))
    responses.append(response)
  target_metric = get_server_metric("grpc_server_msg_sent")
  # None streaming request has no this metrics
  assert target_metric.samples == []
  assert len(responses) == target_count


@pytest.mark.asyncio
@pytest.mark.parametrize("number_of_res", [1, 10, 100])
async def test_grpc_server_msg_sent_with_unary_stream(
    number_of_res, grpc_server, grpc_stub
):  # pylint: disable=unused-argument
  responses = []
  async for response in grpc_stub.SayHelloUnaryStream(
          hello_world_pb2.MultipleHelloResRequest(
              name="unary stream", res=number_of_res
          )
      ):
    responses.append(response)
  target_metric = get_server_metric("grpc_server_msg_sent")
  assert target_metric.samples[0].value == number_of_res
  assert len(responses) == number_of_res


@pytest.mark.asyncio
@pytest.mark.parametrize("number_of_names", [1, 10, 100])
async def test_grpc_server_msg_sent_with_stream_unary(
    number_of_names, grpc_server, grpc_stub, stream_request_generator
):  # pylint: disable=unused-argument
  responses = []
  responses.append(await grpc_stub.SayHelloStreamUnary(
      stream_request_generator(number_of_names)
  ))
  target_metric = get_server_metric("grpc_server_msg_sent")
  assert target_metric.samples == []
  assert len(responses) > 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "number_of_names, number_of_res", [(1, 10), (10, 100), (100, 100)]
)
async def test_grpc_server_msg_sent_with_bidi_stream(
    number_of_names, number_of_res, grpc_server, grpc_stub, bidi_request_generator
):  # pylint: disable=unused-argument
  responses = []
  async for response in grpc_stub.SayHelloBidiStream(
          bidi_request_generator(number_of_names, number_of_res)
      ):
        responses.append(response)
  target_metric = get_server_metric("grpc_server_msg_sent")
  assert target_metric.samples[0].value == number_of_names * number_of_res
  assert len(responses) == number_of_names * number_of_res
