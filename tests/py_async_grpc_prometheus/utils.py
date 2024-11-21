import requests
from prometheus_client.parser import text_string_to_metric_families


def get_server_metric(metric_name, port=50052):
    metrics = list(
        text_string_to_metric_families(
            requests.get(f"http://localhost:{port}/metrics", timeout=5).text
        )
    )
    target_metric = list(filter(lambda x: x.name == metric_name, metrics))
    assert len(target_metric) == 1
    return target_metric[0]
