"""
Query profiler for tracking execution times.
"""

import logging
import time
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ExecutionMetric(BaseModel):
    """Record of a single execution metric."""

    name: str = Field(..., description="Operation name")
    duration_ms: float = Field(..., description="Duration in milliseconds")
    timestamp: float = Field(..., description="Execution timestamp")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class QueryProfiler:
    """
    Profile query and operation execution times.

    Tracks:
    - Individual execution times
    - Aggregate statistics
    - Slow query detection
    - Performance trends
    """

    def __init__(self, ttl_minutes: Optional[int] = None):
        """
        Initialize the profiler.

        Args:
            ttl_minutes: Optional TTL for metrics (currently unused)
        """
        self.metrics: Dict[str, List[ExecutionMetric]] = {}
        self.ttl_minutes = ttl_minutes
        self._executions: Dict[str, List[float]] = {}  # For backward compatibility

    def profile(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Decorator to profile a function.

        Args:
            func: Function to profile

        Returns:
            Decorated function
        """

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            operation_name = func.__name__
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start_time) * 1000  # Convert to ms

                metric = ExecutionMetric(
                    name=operation_name, duration_ms=duration, timestamp=start_time
                )

                self._record_metric(operation_name, metric)
                logger.debug(f"Profiled {operation_name}: {duration:.2f}ms")

                return result
            except Exception as e:
                duration = (time.time() - start_time) * 1000

                metric = ExecutionMetric(
                    name=operation_name, duration_ms=duration, timestamp=start_time, error=str(e)
                )

                self._record_metric(operation_name, metric)
                logger.error(f"Error in {operation_name}: {e}")
                raise

        return wrapper

    def _record_metric(self, operation_name: str, metric: ExecutionMetric) -> None:
        """Record a metric."""
        if operation_name not in self.metrics:
            self.metrics[operation_name] = []
        self.metrics[operation_name].append(metric)

    def get_stats(self, operation_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get profiling statistics.

        Args:
            operation_name: Optional operation to filter

        Returns:
            Statistics dictionary
        """
        if operation_name:
            if operation_name not in self.metrics:
                return {}

            durations = [m.duration_ms for m in self.metrics[operation_name]]
            if not durations:
                return {}

            return {
                "operation": operation_name,
                "count": len(durations),
                "total_ms": sum(durations),
                "avg_ms": sum(durations) / len(durations),
                "min_ms": min(durations),
                "max_ms": max(durations),
                "errors": sum(1 for m in self.metrics[operation_name] if m.error),
            }

        # Return all stats
        stats = {}
        for op in self.metrics:
            stats[op] = self.get_stats(op)

        return stats

    def get_slow_queries(self, threshold_ms: float = 1000) -> List[ExecutionMetric]:
        """
        Get queries that exceeded threshold.

        Args:
            threshold_ms: Threshold in milliseconds

        Returns:
            List of slow execution metrics
        """
        slow = []
        for metrics in self.metrics.values():
            slow.extend([m for m in metrics if m.duration_ms > threshold_ms])

        return sorted(slow, key=lambda m: m.duration_ms, reverse=True)

    def reset(self) -> None:
        """Reset all profiling data."""
        self.metrics = {}
        self._executions = {}
        logger.info("Reset profiler data")

    def clear(self, operation_name: str) -> None:
        """Clear metrics for a specific operation."""
        if operation_name in self.metrics:
            del self.metrics[operation_name]
            logger.info(f"Cleared metrics for {operation_name}")
