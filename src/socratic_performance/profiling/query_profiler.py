"""Query Profiler - Database query profiling and performance monitoring."""

import functools
import logging
import time
from typing import Any, Callable, Dict

logger = logging.getLogger(__name__)


class QueryProfiler:
    """Profile database queries for performance optimization"""

    def __init__(self):
        self.queries = []
        logger.debug("QueryProfiler initialized")

    def profile(self, func: Callable) -> Callable:
        """Decorator to profile function execution"""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = (time.time() - start) * 1000  # ms

            query_info = {
                "function": func.__name__,
                "elapsed_ms": round(elapsed, 2),
                "timestamp": time.time(),
            }

            self.queries.append(query_info)

            if elapsed > 100:  # Slow query threshold
                logger.warning(f"Slow query: {func.__name__} took {elapsed:.2f}ms")

            return result

        return wrapper

    def get_stats(self) -> Dict[str, Any]:
        """Get query statistics"""
        if not self.queries:
            return {"total": 0, "avg_ms": 0.0, "slowest_queries": []}

        times = [q["elapsed_ms"] for q in self.queries]
        return {
            "total": len(self.queries),
            "avg_ms": round(sum(times) / len(times), 2),
            "min_ms": min(times),
            "max_ms": max(times),
            "slowest_queries": sorted(self.queries, key=lambda x: x["elapsed_ms"], reverse=True)[
                :5
            ],
        }

    def reset(self):
        """Reset profiling data"""
        self.queries.clear()
        logger.info("QueryProfiler reset")
