"""
Performance metrics collection and reporting.
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class PerformanceMetrics(BaseModel):
    """Comprehensive performance metrics."""

    cpu_usage: float = Field(default=0.0, description="CPU usage percentage")
    memory_usage: float = Field(default=0.0, description="Memory usage percentage")
    avg_response_time_ms: float = Field(default=0.0, description="Average response time")
    p95_response_time_ms: float = Field(default=0.0, description="95th percentile response time")
    p99_response_time_ms: float = Field(default=0.0, description="99th percentile response time")
    requests_per_second: float = Field(default=0.0, description="Requests per second")
    error_rate: float = Field(default=0.0, description="Error rate percentage")
    cache_hit_ratio: float = Field(default=0.0, description="Cache hit ratio percentage")
    db_query_time_ms: float = Field(default=0.0, description="Average DB query time")


class MetricsCollector:
    """
    Collect and aggregate performance metrics.

    Gathers metrics from various sources:
    - Query profiler
    - Cache statistics
    - System resources
    """

    def __init__(self) -> None:
        """Initialize metrics collector."""
        self.metrics_history: list[Dict[str, Any]] = []

    def collect(
        self,
        profiler_stats: Optional[Dict[str, Any]] = None,
        cache_stats: Optional[Dict[str, Any]] = None,
        system_stats: Optional[Dict[str, Any]] = None,
    ) -> PerformanceMetrics:
        """
        Collect metrics from various sources.

        Args:
            profiler_stats: Query profiler statistics
            cache_stats: Cache statistics
            system_stats: System resource statistics

        Returns:
            Aggregated performance metrics
        """
        metrics = PerformanceMetrics()

        # Extract cache metrics
        if cache_stats:
            metrics.cache_hit_ratio = cache_stats.get("hit_ratio", 0.0)

        # Extract profiler metrics
        if profiler_stats:
            # Calculate average response time from all operations
            durations = []
            for op_stats in profiler_stats.values():
                if isinstance(op_stats, dict) and "avg_ms" in op_stats:
                    durations.append(op_stats["avg_ms"])

            if durations:
                metrics.avg_response_time_ms = sum(durations) / len(durations)

        # Extract system metrics
        if system_stats:
            metrics.cpu_usage = system_stats.get("cpu_usage", 0.0)
            metrics.memory_usage = system_stats.get("memory_usage", 0.0)
            metrics.requests_per_second = system_stats.get("requests_per_second", 0.0)
            metrics.error_rate = system_stats.get("error_rate", 0.0)

        self.metrics_history.append(metrics.model_dump())
        return metrics

    def get_trend(self, metric_name: str, window: int = 10) -> list[float]:
        """
        Get trend for a metric over time.

        Args:
            metric_name: Name of metric to track
            window: Number of recent measurements to return

        Returns:
            List of metric values
        """
        values = []
        for entry in self.metrics_history[-window:]:
            if metric_name in entry:
                values.append(entry[metric_name])
        return values

    def is_degraded(self, metrics: PerformanceMetrics, thresholds: Dict[str, float]) -> bool:
        """
        Check if performance is degraded.

        Args:
            metrics: Performance metrics
            thresholds: Threshold dictionary with metric names and limits

        Returns:
            True if any metric exceeds threshold
        """
        for metric_name, threshold in thresholds.items():
            if hasattr(metrics, metric_name):
                value = getattr(metrics, metric_name)
                if value > threshold:
                    return True
        return False
