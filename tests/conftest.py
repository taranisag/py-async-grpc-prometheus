import asyncio
import threading
from concurrent import futures
import threading
import asyncio
import pytest
import pytest_asyncio
import grpc
from grpc import aio
from prometheus_client import exposition, registry

from py_async_grpc_prometheus.prometheus_async_client_interceptor import PromAsyncClientInterceptor
from py_async_grpc_prometheus.prometheus_async_server_interceptor import PromAsyncServerInterceptor
from tests.integration.hello_world import hello_world_pb2_grpc as hello_world_grpc
from tests.integration.hello_world.hello_world_server import Greeter
from tests.integration.hello_world import hello_world_pb2

def start_prometheus_server(port, prom_registry=registry.REGISTRY):
  app = exposition.make_wsgi_app(prom_registry)
  httpd = exposition.make_server(
      "",
      port,
      app,
      exposition.ThreadingWSGIServer,
      handler_class=exposition._SilentHandler  # pylint: disable=protected-access
  )
  t = threading.Thread(target=httpd.serve_forever)
  t.start()
  return httpd

@pytest_asyncio.fixture(scope='function')
async def grpc_legacy_server():
  prom_registry = registry.CollectorRegistry(auto_describe=True)
  server = aio.server(futures.ThreadPoolExecutor(max_workers=2),
                       interceptors=(
                           PromAsyncServerInterceptor(
                               legacy=True,
                               enable_handling_time_histogram=True,
                               registry=prom_registry
                           ),
                       ))
  hello_world_grpc.add_GreeterServicer_to_server(Greeter(), server)
  server.add_insecure_port("[::]:50051")
  await server.start()
  prom_server = start_prometheus_server(50052, prom_registry)

  yield server
  await server.stop(0)
  prom_server.shutdown()
  prom_server.server_close()

@pytest_asyncio.fixture(scope='function')
async def grpc_server_with_exception_handling():
  prom_registry = registry.CollectorRegistry(auto_describe=True)
  server = aio.server(futures.ThreadPoolExecutor(max_workers=2),
                       interceptors=(
                           PromAsyncServerInterceptor(
                               skip_exceptions=True,
                               enable_handling_time_histogram=True,
                               registry=prom_registry
                           ),
                       ))
  hello_world_grpc.add_GreeterServicer_to_server(Greeter(), server)
  server.add_insecure_port("[::]:50051")
  await server.start()
  prom_server = start_prometheus_server(50052, prom_registry)

  yield server
  await server.stop(0)
  prom_server.shutdown()
  prom_server.server_close()

class GrpcStub:
    def __init__(self, stub, prom_server_port, prom_client_port):
        self.stub = stub
        self.prom_server_port = prom_server_port
        self.prom_client_port = prom_client_port

@pytest_asyncio.fixture(scope="function")
async def grpc_stub():
    prom_registry = registry.CollectorRegistry(auto_describe=True)
    server = aio.server(
        futures.ThreadPoolExecutor(max_workers=2),
        interceptors=(
            PromAsyncServerInterceptor(
                enable_handling_time_histogram=True, registry=prom_registry
            ),
        ),
    )
    hello_world_grpc.add_GreeterServicer_to_server(Greeter(), server)
    port = server.add_insecure_port("[::]:0")
    await server.start()
    prom_server = start_prometheus_server(0, prom_registry)

    prom_registry = registry.CollectorRegistry(auto_describe=True)
    channel = aio.insecure_channel(
        f"localhost:{port}",
        interceptors=(PromAsyncClientInterceptor(registry=prom_registry, enable_client_handling_time_histogram=True),),
    )
    stub = hello_world_grpc.GreeterStub(channel)
    prom_client_server = start_prometheus_server(0, prom_registry)

    yield GrpcStub(stub, prom_server.server_port, prom_client_server.server_port)

    await channel.close()
    prom_client_server.shutdown()
    prom_client_server.server_close()

    await server.stop(0)
    prom_server.shutdown()
    prom_server.server_close()


@pytest.fixture(scope="module")
def stream_request_generator():
  def _generate_requests(number_of_names):
    for i in range(number_of_names):
      yield hello_world_pb2.HelloRequest(name="{}".format(i))
  return _generate_requests

@pytest.fixture(scope="module")
def bidi_request_generator():
  def _generate_bidi_requests(number_of_names, number_of_res):
    for i in range(number_of_names):
      yield hello_world_pb2.MultipleHelloResRequest(name="{}".format(i), res=number_of_res)
  return _generate_bidi_requests

@pytest_asyncio.fixture(scope='session', autouse=True)
def event_loop(request):
  """Create an instance of the default event loop for each test case."""
  loop = asyncio.get_event_loop_policy().new_event_loop()
  yield loop
  loop.close()
