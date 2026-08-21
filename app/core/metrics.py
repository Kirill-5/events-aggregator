from prometheus_client import Counter, Gauge, Histogram

DEFAULT_BUCKETS = [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]

http_requests_total = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=DEFAULT_BUCKETS,
)

events_provider_requests_total = Counter(
    "events_provider_requests_total",
    "Total number of requests to Events Provider API",
    ["endpoint", "status"],
)

events_provider_request_duration_seconds = Histogram(
    "events_provider_request_duration_seconds",
    "Events Provider API request duration in seconds",
    ["endpoint"],
    buckets=DEFAULT_BUCKETS,
)

events_total = Gauge(
    "events_total",
    "Current number of events in the database",
)

tickets_created_total = Gauge(
    "tickets_created_total",
    "Total number of tickets created in the database",
)

tickets_cancelled_total = Gauge(
    "tickets_cancelled_total",
    "Total number of tickets cancelled in the database",
)

cache_hits_total = Counter(
    "cache_hits_total",
    "Total number of seats cache hits",
)

cache_misses_total = Counter(
    "cache_misses_total",
    "Total number of seats cache misses",
)
