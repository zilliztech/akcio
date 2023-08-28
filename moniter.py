import os
import time

from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, Histogram, Summary

# Define metrics
latencies = {}
latencies['all'] = []

requests_total = Counter('requests_total', 'Cumulative requests', ['name'])
requests_success_total = Counter('requests_success_total', 'Cumulative successful requests', ['name'])
requests_failed_total = Counter('requests_failed_total', 'Cumulative failed requests', ['name'])

endpoint_requests_total = Counter('endpoint_requests_total', 'Cumulative requests of each endpoint', ['name', 'endpoint'])
endpoint_requests_success_total = Counter('endpoint_requests_success_total', 'Cumulative successful requests of each endpoint', ['name', 'endpoint'])
endpoint_requests_failed_total = Counter('endpoint_requests_failed_total', 'Cumulative failed requests of each endpoint', ['name', 'endpoint'])

latency_seconds_histogram = Histogram('latency_seconds_histogram', 'Request process latency histogram', ['name'])
endpoint_latency_seconds_histogram = Histogram(
    'endpoint_latency_seconds_histogram', 'Request process latency histogram of each endpoint', ['name', 'endpoint']
)

latency_seconds_summary = Summary('latency_seconds_summary', 'Request process latency summary', ['name'])
endpoint_latency_seconds_summary = Summary(
    'endpoint_latency_seconds_summary', 'Request process latency summary of each endpoint', ['name', 'endpoint']
)


def enable_moniter(app, max_observation, name):

    # Define middleware to collect metrics
    class RequestMetricsMiddleware(BaseHTTPMiddleware):
        """
        Middleware to process requests.
        """
        async def dispatch(self, request, call_next):
            path = request.scope.get('path')
            is_req = path != '/metrics'

            if not is_req:
                try:
                    response = await call_next(request)
                    return response
                except Exception as e:
                    raise e

            begin = time.time()
            requests_total.labels(name).inc()
            endpoint_requests_total.labels(name, path).inc()
            try:
                response = await call_next(request)
                if response.status_code / 100 < 4:
                    requests_success_total.labels(name).inc()
                    endpoint_requests_success_total.labels(name, path).inc()
                    end = time.time()
                    if path in latencies:
                        latencies[path].append(end - begin)
                        latencies[path] = latencies[path][-max_observation:]
                    else:
                        latencies[path] = [end - begin]
                    latencies['all'].append(end - begin)
                    latencies['all'] = latencies['all'][-max_observation:]
                    latency_seconds_histogram.labels(name).observe(end - begin)
                    endpoint_latency_seconds_histogram.labels(name, path).observe(end - begin)
                    latency_seconds_summary.labels(name).observe(end - begin)
                    endpoint_latency_seconds_summary.labels(name, path).observe(end - begin)
                    return response
                else:
                    requests_failed_total.labels(name).inc()
                    endpoint_requests_failed_total.labels(name, path).inc()
            except Exception as e:
                requests_failed_total.labels(name).inc()
                endpoint_requests_failed_total.labels(name, path).inc()
                raise e

    app.add_middleware(RequestMetricsMiddleware)