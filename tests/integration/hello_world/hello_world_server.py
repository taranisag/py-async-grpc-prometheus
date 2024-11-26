import logging
import time
import asyncio
from concurrent import futures

import grpc
from grpc import aio
from prometheus_client import start_http_server

import tests.integration.hello_world.hello_world_pb2 as hello_world_pb2
import tests.integration.hello_world.hello_world_pb2_grpc as hello_world_grpc
from py_async_grpc_prometheus.prometheus_async_server_interceptor import PromAsyncServerInterceptor

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
_LOGGER = logging.getLogger(__name__)

class Greeter(hello_world_grpc.GreeterServicer):

  async def SayHello(self, request, context):
    if request.name == "invalid":
      context.abort(grpc.StatusCode.INVALID_ARGUMENT, 'Consarnit!')
    if request.name == "rpcError":
      context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
      context.set_details('Consarnit!')
      raise grpc.RpcError()
    if request.name == "unknownError":
      raise Exception(request.name)
    if request.name == "delay":
      await asyncio.sleep(2)
    return hello_world_pb2.HelloReply(message="Hello, %s!" % request.name)

  async def SayHelloUnaryStream(self, request, context):
    if request.name == "invalid":
      context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
      context.set_details('Consarnit!')
      return
    if request.name == "delay":
      await asyncio.sleep(2)
    for i in range(request.res):
      yield hello_world_pb2.HelloReply(
          message="Hello, %s %s!" % (request.name, i)
      )
    return

  async def SayHelloStreamUnary(self, request_iterator, context):
    names = ""
    async for request in request_iterator:
      if request.name == "delay":
        await asyncio.sleep(2)
      names += request.name + " "
    return hello_world_pb2.HelloReply(message="Hello, %s!" % names)

  async def SayHelloBidiStream(self, request_iterator, context):
    async for request in request_iterator:
      for i in range(request.res):
        yield hello_world_pb2.HelloReply(message="Hello, %s %s!" % (request.name, i))


async def serve():
  logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
  _LOGGER.info("Starting py-async-grpc-promtheus hello word server")
  server = aio.server(futures.ThreadPoolExecutor(max_workers=10),
                       interceptors=(
                           PromAsyncServerInterceptor(
                               enable_handling_time_histogram=True,
                               skip_exceptions=True
                           ),
                       ))
  hello_world_grpc.add_GreeterServicer_to_server(Greeter(), server)
  server.add_insecure_port("[::]:50051")
  await server.start()
  start_http_server(50052)

  _LOGGER.info("Started py-async-grpc-promtheus hello word server, grpc at localhost:50051, "
               "metrics at http://localhost:50052")
  try:
    await server.wait_for_termination()
  except KeyboardInterrupt:
    await server.stop(0)


if __name__ == "__main__":
  loop = asyncio.get_event_loop()
  loop.run_until_complete(serve())
  loop.close()
