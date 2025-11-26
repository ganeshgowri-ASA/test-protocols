"""
Health Checks and Monitoring for Railway Production Deployment
===============================================================
Enterprise-grade health checking, metrics collection, and performance
monitoring with Railway platform integration.
"""

import os
import time
import threading
import psutil
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from collections import deque
from functools import wraps
import json


@dataclass
class HealthStatus:
    """Health check status result"""
    name: str
    status: str  # healthy, degraded, unhealthy
    latency_ms: float
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "latency_ms": round(self.latency_ms, 2),
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp
        }


class HealthChecker:
    """
    Comprehensive health checking system.

    Features:
    - Multiple health check types (liveness, readiness, startup)
    - Component-level health checks
    - Dependency health monitoring
    - Automatic degradation detection
    """

    def __init__(self):
        self._checks: Dict[str, Callable] = {}
        self._startup_time = datetime.utcnow()
        self._ready = False
        self._lock = threading.Lock()

    def register_check(self, name: str, check_func: Callable) -> None:
        """Register a health check function"""
        with self._lock:
            self._checks[name] = check_func

    def unregister_check(self, name: str) -> None:
        """Unregister a health check"""
        with self._lock:
            self._checks.pop(name, None)

    def set_ready(self, ready: bool = True) -> None:
        """Set the readiness state"""
        self._ready = ready

    def check_liveness(self) -> Dict[str, Any]:
        """
        Liveness check - is the service alive?

        Returns minimal response to indicate the service is running.
        """
        return {
            "status": "alive",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": self._get_uptime()
        }

    def check_readiness(self) -> Dict[str, Any]:
        """
        Readiness check - is the service ready to accept traffic?

        Checks all registered health checks.
        """
        if not self._ready:
            return {
                "status": "not_ready",
                "message": "Service is starting up",
                "timestamp": datetime.utcnow().isoformat()
            }

        results = []
        overall_status = "healthy"

        with self._lock:
            checks = dict(self._checks)

        for name, check_func in checks.items():
            try:
                start_time = time.time()
                result = check_func()
                latency_ms = (time.time() - start_time) * 1000

                if isinstance(result, dict):
                    status = HealthStatus(
                        name=name,
                        status=result.get("status", "healthy"),
                        latency_ms=latency_ms,
                        message=result.get("message", ""),
                        details=result.get("details", {})
                    )
                else:
                    status = HealthStatus(
                        name=name,
                        status="healthy" if result else "unhealthy",
                        latency_ms=latency_ms
                    )

            except Exception as e:
                status = HealthStatus(
                    name=name,
                    status="unhealthy",
                    latency_ms=0,
                    message=str(e)
                )

            results.append(status.to_dict())

            if status.status == "unhealthy":
                overall_status = "unhealthy"
            elif status.status == "degraded" and overall_status != "unhealthy":
                overall_status = "degraded"

        return {
            "status": overall_status,
            "checks": results,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": self._get_uptime()
        }

    def check_startup(self) -> Dict[str, Any]:
        """
        Startup check - has the service completed initialization?
        """
        return {
            "status": "ready" if self._ready else "starting",
            "started_at": self._startup_time.isoformat(),
            "uptime_seconds": self._get_uptime()
        }

    def _get_uptime(self) -> float:
        """Get service uptime in seconds"""
        return (datetime.utcnow() - self._startup_time).total_seconds()

    def get_full_status(self) -> Dict[str, Any]:
        """Get complete health status including system metrics"""
        readiness = self.check_readiness()

        # Add system metrics
        try:
            system_metrics = {
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory": {
                    "used_percent": psutil.virtual_memory().percent,
                    "available_mb": psutil.virtual_memory().available / (1024 * 1024)
                },
                "disk": {
                    "used_percent": psutil.disk_usage('/').percent
                }
            }
        except Exception:
            system_metrics = {}

        return {
            **readiness,
            "system": system_metrics,
            "service": {
                "name": os.getenv("RAILWAY_SERVICE_NAME", "solar-pv-lims"),
                "environment": os.getenv("RAILWAY_ENVIRONMENT", "development"),
                "deployment_id": os.getenv("RAILWAY_DEPLOYMENT_ID", "local"),
                "version": os.getenv("APP_VERSION", "1.0.0")
            }
        }


class MetricsCollector:
    """
    Metrics collection and aggregation system.

    Features:
    - Counter, gauge, and histogram metrics
    - Time-series data with configurable retention
    - Thread-safe operations
    - Export in various formats
    """

    def __init__(self, retention_minutes: int = 60):
        self._lock = threading.Lock()
        self._counters: Dict[str, int] = {}
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, deque] = {}
        self._timeseries: Dict[str, deque] = {}
        self._retention = timedelta(minutes=retention_minutes)
        self._start_time = datetime.utcnow()

    def increment(self, name: str, value: int = 1, labels: Dict[str, str] = None):
        """Increment a counter"""
        key = self._make_key(name, labels)
        with self._lock:
            self._counters[key] = self._counters.get(key, 0) + value

    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """Set a gauge value"""
        key = self._make_key(name, labels)
        with self._lock:
            self._gauges[key] = value

            # Store in timeseries
            if key not in self._timeseries:
                self._timeseries[key] = deque(maxlen=1000)
            self._timeseries[key].append({
                "timestamp": datetime.utcnow().isoformat(),
                "value": value
            })

    def observe(self, name: str, value: float, labels: Dict[str, str] = None):
        """Record a value in a histogram"""
        key = self._make_key(name, labels)
        with self._lock:
            if key not in self._histograms:
                self._histograms[key] = deque(maxlen=10000)
            self._histograms[key].append({
                "timestamp": datetime.utcnow().isoformat(),
                "value": value
            })

    def get_counter(self, name: str, labels: Dict[str, str] = None) -> int:
        """Get counter value"""
        key = self._make_key(name, labels)
        return self._counters.get(key, 0)

    def get_gauge(self, name: str, labels: Dict[str, str] = None) -> Optional[float]:
        """Get gauge value"""
        key = self._make_key(name, labels)
        return self._gauges.get(key)

    def get_histogram_stats(self, name: str, labels: Dict[str, str] = None) -> Dict[str, float]:
        """Get histogram statistics"""
        key = self._make_key(name, labels)
        with self._lock:
            if key not in self._histograms or not self._histograms[key]:
                return {}

            values = [item["value"] for item in self._histograms[key]]
            sorted_values = sorted(values)
            n = len(sorted_values)

            return {
                "count": n,
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / n,
                "p50": sorted_values[int(n * 0.5)],
                "p90": sorted_values[int(n * 0.9)],
                "p99": sorted_values[int(n * 0.99)] if n >= 100 else sorted_values[-1]
            }

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics"""
        with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {
                    k: self.get_histogram_stats(k.split("{")[0])
                    for k in self._histograms
                },
                "uptime_seconds": (datetime.utcnow() - self._start_time).total_seconds()
            }

    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format"""
        lines = []

        with self._lock:
            for key, value in self._counters.items():
                name, labels = self._parse_key(key)
                labels_str = self._format_labels(labels)
                lines.append(f"{name}{labels_str} {value}")

            for key, value in self._gauges.items():
                name, labels = self._parse_key(key)
                labels_str = self._format_labels(labels)
                lines.append(f"{name}{labels_str} {value}")

        return "\n".join(lines)

    def _make_key(self, name: str, labels: Dict[str, str] = None) -> str:
        """Create a unique key for a metric"""
        if not labels:
            return name
        label_str = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"

    def _parse_key(self, key: str) -> tuple:
        """Parse a metric key into name and labels"""
        if "{" not in key:
            return key, {}

        name = key[:key.index("{")]
        labels_str = key[key.index("{") + 1:key.rindex("}")]
        labels = {}

        for part in labels_str.split(","):
            if "=" in part:
                k, v = part.split("=", 1)
                labels[k] = v.strip('"')

        return name, labels

    def _format_labels(self, labels: Dict[str, str]) -> str:
        """Format labels for Prometheus export"""
        if not labels:
            return ""
        return "{" + ",".join(f'{k}="{v}"' for k, v in sorted(labels.items())) + "}"

    def reset(self):
        """Reset all metrics"""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
            self._timeseries.clear()


class PerformanceMonitor:
    """
    Application performance monitoring.

    Features:
    - Request/response timing
    - Throughput measurement
    - Error rate tracking
    - Resource utilization monitoring
    """

    def __init__(self, metrics: MetricsCollector = None):
        self.metrics = metrics or MetricsCollector()
        self._active_requests = 0
        self._lock = threading.Lock()

    def record_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float
    ):
        """Record HTTP request metrics"""
        labels = {"method": method, "status": str(status_code)}

        self.metrics.increment("http_requests_total", labels=labels)
        self.metrics.observe("http_request_duration_ms", duration_ms, labels={"path": path})

        if status_code >= 500:
            self.metrics.increment("http_errors_total", labels={"type": "5xx"})
        elif status_code >= 400:
            self.metrics.increment("http_errors_total", labels={"type": "4xx"})

    def record_db_query(self, duration_ms: float, success: bool = True):
        """Record database query metrics"""
        self.metrics.increment("db_queries_total", labels={"success": str(success).lower()})
        self.metrics.observe("db_query_duration_ms", duration_ms)

        if not success:
            self.metrics.increment("db_errors_total")

    def record_cache_operation(self, operation: str, hit: bool):
        """Record cache operation metrics"""
        self.metrics.increment(
            "cache_operations_total",
            labels={"operation": operation, "hit": str(hit).lower()}
        )

    def record_queue_operation(self, queue_name: str, operation: str):
        """Record queue operation metrics"""
        self.metrics.increment(
            "queue_operations_total",
            labels={"queue": queue_name, "operation": operation}
        )

    def track_active_requests(self):
        """Context manager to track active requests"""
        class RequestTracker:
            def __init__(tracker_self):
                tracker_self.monitor = self

            def __enter__(tracker_self):
                with self._lock:
                    self._active_requests += 1
                    self.metrics.set_gauge("http_active_requests", self._active_requests)

            def __exit__(tracker_self, *args):
                with self._lock:
                    self._active_requests -= 1
                    self.metrics.set_gauge("http_active_requests", self._active_requests)

        return RequestTracker()

    def update_system_metrics(self):
        """Update system resource metrics"""
        try:
            self.metrics.set_gauge("system_cpu_percent", psutil.cpu_percent())
            self.metrics.set_gauge("system_memory_percent", psutil.virtual_memory().percent)
            self.metrics.set_gauge("system_memory_available_mb",
                                  psutil.virtual_memory().available / (1024 * 1024))
            self.metrics.set_gauge("system_disk_percent", psutil.disk_usage('/').percent)

            # Process-specific metrics
            process = psutil.Process()
            self.metrics.set_gauge("process_memory_mb",
                                  process.memory_info().rss / (1024 * 1024))
            self.metrics.set_gauge("process_cpu_percent", process.cpu_percent())
            self.metrics.set_gauge("process_threads", process.num_threads())

        except Exception:
            pass

    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        request_stats = self.metrics.get_histogram_stats("http_request_duration_ms")
        db_stats = self.metrics.get_histogram_stats("db_query_duration_ms")

        return {
            "requests": {
                "total": self.metrics.get_counter("http_requests_total"),
                "active": self._active_requests,
                "duration": request_stats
            },
            "database": {
                "queries": self.metrics.get_counter("db_queries_total"),
                "errors": self.metrics.get_counter("db_errors_total"),
                "duration": db_stats
            },
            "errors": {
                "5xx": self.metrics.get_counter("http_errors_total", {"type": "5xx"}),
                "4xx": self.metrics.get_counter("http_errors_total", {"type": "4xx"})
            }
        }


# Decorators
def timed(metric_name: str = None, monitor: PerformanceMonitor = None):
    """Decorator to time function execution"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            except Exception:
                success = False
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000
                if monitor:
                    name = metric_name or f"function_{func.__name__}"
                    monitor.metrics.observe(name, duration_ms, {"success": str(success)})
        return wrapper
    return decorator


# Global instances
health_checker = HealthChecker()
metrics_collector = MetricsCollector()
performance_monitor = PerformanceMonitor(metrics_collector)


# Railway health check endpoints setup
def setup_health_routes(app):
    """
    Setup health check routes for Railway.

    Railway expects:
    - /health for general health check
    - /healthz for Kubernetes-style liveness
    - /ready for readiness check
    """
    from flask import Flask, jsonify

    @app.route('/health')
    def health():
        return jsonify(health_checker.get_full_status())

    @app.route('/healthz')
    def healthz():
        return jsonify(health_checker.check_liveness())

    @app.route('/ready')
    def ready():
        result = health_checker.check_readiness()
        status_code = 200 if result["status"] == "healthy" else 503
        return jsonify(result), status_code

    @app.route('/metrics')
    def metrics():
        return metrics_collector.export_prometheus(), 200, {
            'Content-Type': 'text/plain; charset=utf-8'
        }


# Streamlit health check (for Streamlit apps)
def streamlit_health_widget():
    """Display health status in Streamlit"""
    import streamlit as st

    status = health_checker.get_full_status()

    if status["status"] == "healthy":
        st.success(f"System Status: {status['status'].upper()}")
    elif status["status"] == "degraded":
        st.warning(f"System Status: {status['status'].upper()}")
    else:
        st.error(f"System Status: {status['status'].upper()}")

    with st.expander("Health Details"):
        st.json(status)
