"""Interceptor a client call with prometheus"""

from timeit import default_timer

from grpc.aio import UnaryUnaryClientInterceptor, UnaryStreamClientInterceptor, StreamUnaryClientInterceptor, StreamStreamClientInterceptor
from prometheus_client.registry import REGISTRY

from py_async_grpc_prometheus import grpc_utils
from py_async_grpc_prometheus.client_metrics import init_metrics


class _PromAsyncUnaryUnaryClientInterceptor(UnaryUnaryClientInterceptor):
    """
    Intercept gRPC Unary Unary client requests.
    """

    def __init__(
        self,
        metrics,
        enable_client_handling_time_histogram=False,
        enable_client_stream_receive_time_histogram=False,
        enable_client_stream_send_time_histogram=False,
        legacy=False,
    ):
        self._enable_client_handling_time_histogram = enable_client_handling_time_histogram
        self._enable_client_stream_receive_time_histogram = enable_client_stream_receive_time_histogram
        self._enable_client_stream_send_time_histogram = enable_client_stream_send_time_histogram
        self._legacy = legacy
        self._metrics = metrics

    async def intercept_unary_unary(self, continuation, client_call_details, request):
        grpc_service_name, grpc_method_name, _ = grpc_utils.split_method_call(client_call_details)
        grpc_type = grpc_utils.UNARY

        self._metrics["grpc_client_started_counter"].labels(
            grpc_type=grpc_type,
            grpc_service=grpc_service_name,
            grpc_method=grpc_method_name).inc()

        start = default_timer()
        handler = await continuation(client_call_details, request)

        await handler

        if self._legacy:
            self._metrics[
                "legacy_grpc_client_completed_latency_seconds_histogram"
            ].labels(
                grpc_type=grpc_type,
                grpc_service=grpc_service_name,
                grpc_method=grpc_method_name,
            ).observe(max(default_timer() - start, 0))
        elif self._enable_client_handling_time_histogram:
            self._metrics["grpc_client_handled_histogram"].labels(
                grpc_type=grpc_type,
                grpc_service=grpc_service_name,
                grpc_method=grpc_method_name,
            ).observe(max(default_timer() - start, 0))

        code = await handler.code()

        if self._legacy:
            self._metrics["legacy_grpc_client_completed_counter"].labels(
                grpc_type=grpc_type,
                grpc_service=grpc_service_name,
                grpc_method=grpc_method_name,
                code=code.name).inc()
        else:
            self._metrics["grpc_client_handled_counter"].labels(
                grpc_type=grpc_type,
                grpc_service=grpc_service_name,
                grpc_method=grpc_method_name,
                grpc_code=code.name).inc()

        return handler

class _PromAsyncUnaryStreamClientInterceptor(UnaryStreamClientInterceptor):
    """
    Intercept gRPC Unary Stream client requests.
    """

    def __init__(
        self,
        metrics,
        enable_client_handling_time_histogram=False,
        enable_client_stream_receive_time_histogram=False,
        enable_client_stream_send_time_histogram=False,
        legacy=False,
    ):
        self._enable_client_handling_time_histogram = enable_client_handling_time_histogram
        self._enable_client_stream_receive_time_histogram = enable_client_stream_receive_time_histogram
        self._enable_client_stream_send_time_histogram = enable_client_stream_send_time_histogram
        self._legacy = legacy
        self._metrics = metrics

    async def intercept_unary_stream(self, continuation, client_call_details, request):
        grpc_service_name, grpc_method_name, _ = grpc_utils.split_method_call(client_call_details)
        grpc_type = grpc_utils.SERVER_STREAMING

        self._metrics["grpc_client_started_counter"].labels(
            grpc_type=grpc_type,
            grpc_service=grpc_service_name,
            grpc_method=grpc_method_name,
        ).inc()

        start = default_timer()
        handler = await continuation(client_call_details, request)

        legacy_observer = None
        observer = None
        if self._legacy:
            legacy_observer = self._metrics[
                "legacy_grpc_client_completed_latency_seconds_histogram"
            ].labels(
                grpc_type=grpc_type,
                grpc_service=grpc_service_name,
                grpc_method=grpc_method_name,
            )

        elif self._enable_client_handling_time_histogram:
            observer = self._metrics["grpc_client_handled_histogram"].labels(
                grpc_type=grpc_type,
                grpc_service=grpc_service_name,
                grpc_method=grpc_method_name,
            )

        handler = grpc_utils.wrap_iterator_inc_counter(
            handler,
            self._metrics["grpc_client_stream_msg_received"],
            grpc_type,
            grpc_service_name,
            grpc_method_name,
            observer,
            legacy_observer,
            default_timer,
            start
        )

        if self._enable_client_stream_receive_time_histogram and not self._legacy:
            self._metrics["grpc_client_stream_recv_histogram"].labels(
                grpc_type=grpc_type,
                grpc_service=grpc_service_name,
                grpc_method=grpc_method_name,
            ).observe(max(default_timer() - start, 0))

        return handler

class _PromAsyncStreamUnaryClientInterceptor(StreamUnaryClientInterceptor):
    """
    Intercept gRPC Stream Unary client requests.
    """

    def __init__(
        self,
        metrics,
        enable_client_handling_time_histogram=False,
        enable_client_stream_receive_time_histogram=False,
        enable_client_stream_send_time_histogram=False,
        legacy=False,
    ):
        self._enable_client_handling_time_histogram = enable_client_handling_time_histogram
        self._enable_client_stream_receive_time_histogram = enable_client_stream_receive_time_histogram
        self._enable_client_stream_send_time_histogram = enable_client_stream_send_time_histogram
        self._legacy = legacy
        self._metrics = metrics

    async def intercept_stream_unary(
        self, continuation, client_call_details, request_iterator
    ):
        grpc_service_name, grpc_method_name, _ = grpc_utils.split_method_call(
            client_call_details
        )
        grpc_type = grpc_utils.CLIENT_STREAMING

        iterator_metric = self._metrics["grpc_client_stream_msg_sent"]

        request_iterator = grpc_utils.wrap_iterator_inc_counter(
            request_iterator,
            iterator_metric,
            grpc_type,
            grpc_service_name,
            grpc_method_name,
        )

        start = default_timer()
        handler = await continuation(client_call_details, request_iterator)

        await handler

        if self._legacy:
            self._metrics["grpc_client_started_counter"].labels(
                grpc_type=grpc_type,
                grpc_service=grpc_service_name,
                grpc_method=grpc_method_name,
            ).inc()
            self._metrics[
                "legacy_grpc_client_completed_latency_seconds_histogram"
            ].labels(
                grpc_type=grpc_type,
                grpc_service=grpc_service_name,
                grpc_method=grpc_method_name,
            ).observe(max(default_timer() - start, 0))
        else:
            self._metrics["grpc_client_started_counter"].labels(
                grpc_type=grpc_type,
                grpc_service=grpc_service_name,
                grpc_method=grpc_method_name,
            ).inc()
            if self._enable_client_handling_time_histogram:
                self._metrics["grpc_client_handled_histogram"].labels(
                    grpc_type=grpc_type,
                    grpc_service=grpc_service_name,
                    grpc_method=grpc_method_name,
                ).observe(max(default_timer() - start, 0))

        if self._enable_client_stream_send_time_histogram and not self._legacy:
            self._metrics["grpc_client_stream_send_histogram"].labels(
                grpc_type=grpc_type,
                grpc_service=grpc_service_name,
                grpc_method=grpc_method_name,
            ).observe(max(default_timer() - start, 0))

        return handler


class _PromAsyncStreamStreamClientInterceptor(StreamStreamClientInterceptor):
    """
    Intercept gRPC Stream Stream client requests.
    """

    def __init__(
        self,
        metrics,
        enable_client_handling_time_histogram=False,
        enable_client_stream_receive_time_histogram=False,
        enable_client_stream_send_time_histogram=False,
        legacy=False,
    ):
        self._enable_client_handling_time_histogram = enable_client_handling_time_histogram
        self._enable_client_stream_receive_time_histogram = enable_client_stream_receive_time_histogram
        self._enable_client_stream_send_time_histogram = enable_client_stream_send_time_histogram
        self._legacy = legacy
        self._metrics = metrics

    async def intercept_stream_stream(
        self, continuation, client_call_details, request_iterator
    ):
        grpc_service_name, grpc_method_name, _ = grpc_utils.split_method_call(
            client_call_details
        )
        grpc_type = grpc_utils.BIDI_STREAMING
        start = default_timer()

        iterator_sent_metric = self._metrics["grpc_client_stream_msg_sent"]

        response_iterator = await continuation(
            client_call_details,
            grpc_utils.wrap_iterator_inc_counter(
                request_iterator,
                iterator_sent_metric,
                grpc_type,
                grpc_service_name,
                grpc_method_name,
            ),
        )

        if self._enable_client_stream_send_time_histogram and not self._legacy:
            self._metrics["grpc_client_stream_send_histogram"].labels(
                grpc_type=grpc_type,
                grpc_service=grpc_service_name,
                grpc_method=grpc_method_name,
            ).observe(max(default_timer() - start, 0))

        iterator_received_metric = self._metrics["grpc_client_stream_msg_received"]

        response_iterator = grpc_utils.wrap_iterator_inc_counter(
            response_iterator,
            iterator_received_metric,
            grpc_type,
            grpc_service_name,
            grpc_method_name,
        )

        if self._enable_client_stream_receive_time_histogram and not self._legacy:
            self._metrics["grpc_client_stream_recv_histogram"].labels(
                grpc_type=grpc_type,
                grpc_service=grpc_service_name,
                grpc_method=grpc_method_name,
            ).observe(max(default_timer() - start, 0))

        return response_iterator


class PromAsyncClientInterceptor(_PromAsyncUnaryUnaryClientInterceptor,
                            _PromAsyncUnaryStreamClientInterceptor,
                            _PromAsyncStreamUnaryClientInterceptor,
                            _PromAsyncStreamStreamClientInterceptor):
    """
    Intercept gRPC client requests.
    """
    def __init__(
        self,
        enable_client_handling_time_histogram=False,
        enable_client_stream_receive_time_histogram=False,
        enable_client_stream_send_time_histogram=False,
        legacy=False,
        registry=REGISTRY,
    ):
        metrics = init_metrics(REGISTRY)
        _PromAsyncUnaryUnaryClientInterceptor.__init__(
            self,
            metrics,
            enable_client_handling_time_histogram,
            enable_client_stream_receive_time_histogram,
            enable_client_stream_send_time_histogram,
            legacy,
        )
        _PromAsyncUnaryStreamClientInterceptor.__init__(
            self,
            metrics,
            enable_client_handling_time_histogram,
            enable_client_stream_receive_time_histogram,
            enable_client_stream_send_time_histogram,
            legacy,
        )
        _PromAsyncStreamUnaryClientInterceptor.__init__(
            self,
            metrics,
            enable_client_handling_time_histogram,
            enable_client_stream_receive_time_histogram,
            enable_client_stream_send_time_histogram,
            legacy,
        )
        _PromAsyncStreamStreamClientInterceptor.__init__(
            self,
            metrics,
            enable_client_handling_time_histogram,
            enable_client_stream_receive_time_histogram,
            enable_client_stream_send_time_histogram,
            legacy,
        )



# grpc aio requires a list of interceptors because of the elif chain it currently uses: https://github.com/grpc/grpc/issues/31442
def get_client_interceptors(
    enable_client_handling_time_histogram=False,
    enable_client_stream_receive_time_histogram=False,
    enable_client_stream_send_time_histogram=False,
    legacy=False,
    registry=REGISTRY,
):
    """
    Get a list of client interceptors.
    """
    # In a future grpc version the following could be done
    # if supports_single_interceptor(version(grpc)):
    #   return [PromAsyncClientInterceptor(enable_client_handling_time_histogram, enable_client_stream_receive_time_histogram, enable_client_stream_send_time_histogram, legacy, registry)]
    metrics = init_metrics(registry)
    return [
        _PromAsyncUnaryUnaryClientInterceptor(
            metrics,
            enable_client_handling_time_histogram,
            enable_client_stream_receive_time_histogram,
            enable_client_stream_send_time_histogram,
            legacy,
        ),
        _PromAsyncUnaryStreamClientInterceptor(
            metrics,
            enable_client_handling_time_histogram,
            enable_client_stream_receive_time_histogram,
            enable_client_stream_send_time_histogram,
            legacy,
        ),
        _PromAsyncStreamUnaryClientInterceptor(
            metrics,
            enable_client_handling_time_histogram,
            enable_client_stream_receive_time_histogram,
            enable_client_stream_send_time_histogram,
            legacy,
        ),
        _PromAsyncStreamStreamClientInterceptor(
            metrics,
            enable_client_handling_time_histogram,
            enable_client_stream_receive_time_histogram,
            enable_client_stream_send_time_histogram,
            legacy,
        ),
    ]
