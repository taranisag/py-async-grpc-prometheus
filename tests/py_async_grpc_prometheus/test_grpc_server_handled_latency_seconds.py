from functools import reduce

import pytest

from tests.conftest import GrpcStub
from tests.py_async_grpc_prometheus.utils import get_metric
from tests.integration.hello_world import hello_world_pb2


@pytest.mark.asyncio
@pytest.mark.parametrize("target_count", [1, 10, 100])
async def test_grpc_server_handled_latency_seconds_with_normal(
    target_count, grpc_stub: GrpcStub
):
  responses = []
  for i in range(target_count):
    response = await grpc_stub.stub.SayHello(hello_world_pb2.HelloRequest(name=str(i)))
    responses.append(response)
  target_metric = get_metric("grpc_server_handling_seconds", grpc_stub.prom_server_port)
  assert len(target_metric.samples) > 0
  assert len(responses) == target_count


@pytest.mark.asyncio
@pytest.mark.parametrize("number_of_res", [1, 10, 100])
async def test_grpc_server_handled_latency_seconds_with_unary_stream(
    number_of_res, grpc_stub: GrpcStub
):
  responses = []
  async for response in grpc_stub.stub.SayHelloUnaryStream(
          hello_world_pb2.MultipleHelloResRequest(
              name="unary stream", res=number_of_res
          )
      ):
    responses.append(response)
  target_metric = get_metric("grpc_server_handling_seconds", grpc_stub.prom_server_port)
  # No grpc_server_handled_latency_seconds for streaming response
  assert len(target_metric.samples) > 0
  assert len(responses) == number_of_res


@pytest.mark.asyncio
@pytest.mark.parametrize("number_of_names", [1, 10, 100])
async def test_grpc_server_handled_latency_seconds_with_stream_unary(
    number_of_names, grpc_stub: GrpcStub, stream_request_generator
):
  responses = []
  responses.append(await grpc_stub.stub.SayHelloStreamUnary(
      stream_request_generator(number_of_names)
  ))
  target_metric = get_metric("grpc_server_handling_seconds", grpc_stub.prom_server_port)
  assert len(target_metric.samples) > 0
  assert len(responses) > 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "number_of_names, number_of_res", [(1, 10), (10, 100), (100, 100)]
)
async def test_grpc_server_handled_latency_seconds_with_bidi_stream(
    number_of_names, number_of_res, grpc_stub: GrpcStub, bidi_request_generator
):  # pylint: disable=unused-argument
  responses = []
  async for response in grpc_stub.stub.SayHelloBidiStream(
          bidi_request_generator(number_of_names, number_of_res)
      ):
      responses.append(response)
  target_metric = get_metric("grpc_server_handling_seconds", grpc_stub.prom_server_port)
  assert len(target_metric.samples) > 0
  assert len(responses) == number_of_names * number_of_res


@pytest.mark.asyncio
@pytest.mark.parametrize("target_count", [1, 10, 100])
async def test_legacy_grpc_server_handled_latency_seconds_with_normal(
    target_count, grpc_stub_legacy: GrpcStub
):  # pylint: disable=unused-argument
    responses = []
    for i in range(target_count):
        responses.append(
            await grpc_stub_legacy.stub.SayHello(
                hello_world_pb2.HelloRequest(name=str(i))
            )
        )
    target_metric = get_metric(
        "grpc_server_handled_latency_seconds", grpc_stub_legacy.prom_server_port
    )
    assert (
        reduce(
            lambda acc, x: acc if acc > x.value else x.value,
            list(
                filter(
                    lambda x: x.name == "grpc_server_handled_latency_seconds_bucket",
                    target_metric.samples,
                )
            ),
            0,
        )
        == target_count
    )
    assert (
        reduce(
            lambda acc, x: acc if acc > x.value else x.value,
            list(
                filter(
                    lambda x: x.name == "grpc_server_handled_latency_seconds_count",
                    target_metric.samples,
                )
            ),
            0,
        )
        == target_count
    )
    assert (
        reduce(
            lambda acc, x: acc if acc > x.value else x.value,
            list(
                filter(
                    lambda x: x.name == "grpc_server_handled_latency_seconds_sum",
                    target_metric.samples,
                )
            ),
            0,
        )
        > 0
    )
    assert len(responses) == target_count


@pytest.mark.asyncio
@pytest.mark.parametrize("number_of_res", [1, 10, 100])
async def test_legacy_grpc_server_handled_latency_seconds_with_unary_stream(
    number_of_res, grpc_stub_legacy: GrpcStub
):
    responses = []
    async for response in grpc_stub_legacy.stub.SayHelloUnaryStream(
        hello_world_pb2.MultipleHelloResRequest(name="unary stream", res=number_of_res)
    ):
        responses.append(response)
    target_metric = get_metric(
        "grpc_server_handled_latency_seconds", grpc_stub_legacy.prom_server_port
    )
    assert len(target_metric.samples) > 0
    assert len(responses) == number_of_res


@pytest.mark.asyncio
@pytest.mark.parametrize("number_of_names", [1, 10, 100])
async def test_legacy_grpc_server_handled_latency_seconds_with_stream_unary(
    number_of_names, grpc_stub_legacy: GrpcStub, stream_request_generator
):  # pylint: disable=unused-argument
    responses = []
    responses.append(
        await grpc_stub_legacy.stub.SayHelloStreamUnary(
            stream_request_generator(number_of_names)
        )
    )
    target_metric = get_metric("grpc_server_handled_latency_seconds", grpc_stub_legacy.prom_server_port)
    assert (
        reduce(
            lambda acc, x: acc if acc > x.value else x.value,
            list(
                filter(
                    lambda x: x.name == "grpc_server_handled_latency_seconds_bucket",
                    target_metric.samples,
                )
            ),
            0,
        )
        == 1
    )
    assert (
        reduce(
            lambda acc, x: acc if acc > x.value else x.value,
            list(
                filter(
                    lambda x: x.name == "grpc_server_handled_latency_seconds_count",
                    target_metric.samples,
                )
            ),
            0,
        )
        == 1
    )
    assert (
        reduce(
            lambda acc, x: acc if acc > x.value else x.value,
            list(
                filter(
                    lambda x: x.name == "grpc_server_handled_latency_seconds_sum",
                    target_metric.samples,
                )
            ),
            0,
        )
        > 0
    )
    assert len(responses) > 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "number_of_names, number_of_res", [(1, 10), (10, 100), (100, 100)]
)
async def test_legacy_grpc_server_handled_latency_seconds_with_bidi_stream(
    number_of_names, number_of_res, grpc_stub_legacy: GrpcStub, bidi_request_generator
):  # pylint: disable=unused-argument
    responses = []

    async for response in grpc_stub_legacy.stub.SayHelloBidiStream(
        bidi_request_generator(number_of_names, number_of_res)
    ):
        responses.append(response)
    target_metric = get_metric(
        "grpc_server_handled_latency_seconds", grpc_stub_legacy.prom_server_port
    )
    assert len(target_metric.samples) > 0
    assert len(responses) == number_of_names * number_of_res
