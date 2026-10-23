import logging, structlog
from prometheus_client import Counter, Histogram, generate_latest

REQUESTS = Counter("intelliassist_requests_total", "API requests", ["endpoint", "status"])
LATENCY = Histogram("intelliassist_request_latency_seconds", "Request latency", ["endpoint"])
ESCALATIONS = Counter("intelliassist_escalations_total", "Escalations", ["reason"])
ONLINE_EVAL_FAILURES = Counter("intelliassist_online_eval_failures_total", "Online eval failures", ["check"])

def configure_logging():
    logging.basicConfig(level=logging.INFO)
    structlog.configure(processors=[structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level, structlog.processors.JSONRenderer()],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        cache_logger_on_first_use=True)

def metrics_payload():
    return generate_latest()
