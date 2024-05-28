from unittest.mock import patch

import pytest
import grpc

from tests.py_async_grpc_prometheus.utils import get_server_metric
from tests.integration.hello_world import hello_world_pb2


@pytest.mark.asyncio
@pytest.mark.parametrize("target_count", [1, 10, 100])
async def test_grpc_server_handled_with_server_error(
    target_count, grpc_server, grpc_stub
):  # pylint: disable=unused-argument
  for _ in range(target_count):
    with pytest.raises(Exception):
      await grpc_stub.SayHello(hello_world_pb2.HelloRequest(name="unknownError"))

  target_metric = get_server_metric("grpc_server_handled")
  print(target_metric.samples[0].labels["grpc_code"])
  assert target_metric.samples[0].value == target_count
  assert target_metric.samples[0].labels["grpc_code"] == "UNKNOWN"


@pytest.mark.asyncio
@pytest.mark.parametrize("target_count", [1, 10, 100])
async def test_grpc_server_handled_with_rpc_error(
    target_count, grpc_server, grpc_stub
):  # pylint: disable=unused-argument
  for _ in range(target_count):
    with pytest.raises(grpc.RpcError):
      await grpc_stub.SayHello(hello_world_pb2.HelloRequest(name="rpcError"))

  target_metric = get_server_metric("grpc_server_handled")
  assert target_metric.samples[0].value == target_count
  assert target_metric.samples[0].labels["grpc_code"] == "INVALID_ARGUMENT"


@pytest.mark.asyncio
@pytest.mark.parametrize("target_count", [1, 10, 100])
async def test_grpc_server_handled_with_interceptor_error(
    target_count, grpc_server, grpc_stub
):  # pylint: disable=unused-argument
  for _ in range(target_count):
    with patch(
        'py_async_grpc_prometheus.prometheus_async_server_interceptor.'\
        'PromAsyncServerInterceptor._compute_status_code',
        side_effect=Exception('mocked error')
    ):
      with pytest.raises(Exception):
        await grpc_stub.SayHello(hello_world_pb2.HelloRequest(name="unary"))


@pytest.mark.asyncio
@pytest.mark.parametrize("target_count", [1, 10, 100])
async def test_grpc_server_handled_with_server_error_and_skip_exceptions(
    target_count, grpc_server_with_exception_handling, grpc_stub
):  # pylint: disable=unused-argument
  for _ in range(target_count):
    with pytest.raises(Exception):
      await grpc_stub.SayHello(hello_world_pb2.HelloRequest(name="unknownError"))

  target_metric = get_server_metric("grpc_server_handled")
  assert target_metric.samples == []


@pytest.mark.asyncio
@pytest.mark.parametrize("target_count", [1, 10, 100])
async def test_grpc_server_handled_with_interceptor_error_and_skip_exceptions(
    target_count, grpc_server_with_exception_handling, grpc_stub
):  # pylint: disable=unused-argument
  for _ in range(target_count):
    with patch(
        'py_async_grpc_prometheus.prometheus_async_server_interceptor.'\
        'PromAsyncServerInterceptor._compute_status_code',
        side_effect=Exception('mocked error')
    ):
      response = await grpc_stub.SayHello(
          hello_world_pb2.HelloRequest(name="unary"))
      assert response.message == "Hello, unary!"

  target_metric = get_server_metric("grpc_server_handled")
  assert target_metric.samples == []


@pytest.mark.asyncio
@pytest.mark.parametrize("target_count", [1, 10, 100])
async def test_grpc_server_handled_before_request_error(
    target_count, grpc_server, grpc_stub
):  # pylint: disable=unused-argument
  for _ in range(target_count):
    with patch(
        'py_async_grpc_prometheus.grpc_utils.wrap_iterator_inc_counter',
        side_effect=Exception('mocked error')
    ):
      response = await grpc_stub.SayHello(
          hello_world_pb2.HelloRequest(name="unary")
      )
      assert response.message == "Hello, unary!"
