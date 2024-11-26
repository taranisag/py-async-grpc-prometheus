# py-async-grpc-prometheus

Instrument library to provide prometheus metrics similar to:

- https://github.com/grpc-ecosystem/java-grpc-prometheus
- https://github.com/grpc-ecosystem/go-grpc-prometheus


## Status
Currently, the library has the parity metrics with the Java and Go library.

### Server side:
- grpc_server_started_total
- grpc_server_handled_total
- grpc_server_msg_received_total
- grpc_server_msg_sent_total
- grpc_server_handling_seconds

### Client side:
- grpc_client_started_total
- grpc_client_handled_total
- grpc_client_msg_received_total
- grpc_client_msg_sent_total
- grpc_client_handling_seconds
- grpc_client_msg_recv_handling_seconds
- grpc_client_msg_send_handling_seconds

## How to use

```
pip install py-async-grpc-prometheus
```

## Client side:
Client metrics monitoring is done by intercepting the gPRC channel.

```python
from grpc import aio
from py_async_grpc_prometheus.prometheus_async_client_interceptor import get_client_interceptors

channel = aio.insecure_channel("server:6565",
                                 interceptors=get_client_interceptors())
# Start an end point to expose metrics.
start_http_server(metrics_port)
```

## Server side:
Server metrics are exposed by adding the interceptor when the gRPC server is started. Take a look at
`tests/integration/hello_world/hello_world_client.py` for the complete example.

```python
from grpc import aio
from concurrent import futures
from py_async_grpc_prometheus.prometheus_async_server_interceptor import PromAsyncServerInterceptor
from prometheus_client import start_http_server
```

Start the gRPC server with the interceptor, take a look at
`tests/integration/hello_world/hello_world_server.py` for the complete example.

```python
server = aio.server(futures.ThreadPoolExecutor(max_workers=10),
                       interceptors=(
                           PromAsyncServerInterceptor(),
                       ))
# Start an end point to expose metrics.
start_http_server(metrics_port)
```

## Histograms

[Prometheus histograms](https://prometheus.io/docs/concepts/metric_types/#histogram) are a great way
to measure latency distributions of your RPCs. However, since it is bad practice to have metrics
of [high cardinality](https://prometheus.io/docs/practices/instrumentation/#do-not-overuse-labels)
the latency monitoring metrics are disabled by default. To enable them please call the following
in your interceptor initialization code:

```jsoniq
server = aio.server(futures.ThreadPoolExecutor(max_workers=10),
                       interceptors=(
                           PromAsyncServerInterceptor(enable_handling_time_histogram=True),
                       ))
```

After the call completes, its handling time will be recorded in a [Prometheus histogram](https://prometheus.io/docs/concepts/metric_types/#histogram)
variable `grpc_server_handling_seconds`. The histogram variable contains three sub-metrics:

 * `grpc_server_handling_seconds_count` - the count of all completed RPCs by status and method
 * `grpc_server_handling_seconds_sum` - cumulative time of RPCs by status and method, useful for
   calculating average handling times
 * `grpc_server_handling_seconds_bucket` - contains the counts of RPCs by status and method in respective
   handling-time buckets. These buckets can be used by Prometheus to estimate SLAs (see [here](https://prometheus.io/docs/practices/histograms/))

## Server Side:
- enable_handling_time_histogram: Enables 'grpc_server_handling_seconds'

## Client Side:
- enable_client_handling_time_histogram: Enables 'grpc_client_handling_seconds'
- enable_client_stream_receive_time_histogram: Enables 'grpc_client_msg_recv_handling_seconds'
- enable_client_stream_send_time_histogram: Enables 'grpc_client_msg_send_handling_seconds'

## Legacy metrics:

Metric names have been updated to be in line with those from https://github.com/grpc-ecosystem/go-grpc-prometheus.

The legacy metrics are:

### server side:
- grpc_server_started_total
- grpc_server_handled_total
- grpc_server_handled_latency_seconds
- grpc_server_msg_received_total
- grpc_server_msg_sent_total

### client side:
- grpc_client_started_total
- grpc_client_completed
- grpc_client_completed_latency_seconds
- grpc_client_msg_sent_total
- grpc_client_msg_received_total

In order to be able to use these legacy metrics for backwards compatibility, the `legacy` flag can be set to `True` when initialising the server/client interceptors

For example, to enable the server side legacy metrics:
```jsoniq
server = aio.server(futures.ThreadPoolExecutor(max_workers=10),
                       interceptors=(
                           PromAsyncServerInterceptor(legacy=True),
                       ))
```

## How to run and test
```sh
make initialize-development
make test
```

## TODO:
- Test prometheus_async_client_interceptor

## Reference
- https://grpc.io/grpc/python/grpc.html
- https://github.com/census-instrumentation/opencensus-python/blob/master/opencensus/trace/ext/grpc/utils.py
- https://github.com/opentracing-contrib/python-grpc/blob/b4bdc7ce81fa75ede00f7c6bcf5dab8fae47332a/grpc_opentracing/grpcext/grpc_interceptor/server_interceptor.py

