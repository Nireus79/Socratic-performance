from __future__ import annotations

"""
Socratic Performance - Performance Monitoring, Query Profiling, and TTL Caching

Extracted from Socrates v1.3.3
"""

from .checker import SubscriptionChecker
from .query_profiler import QueryProfiler, QueryStats, get_profiler, profile_query
from .tiers import TierLimits
from .ttl_cache import TTLCache, cached

__version__ = "0.3.0"
__all__ = [
    "SubscriptionChecker",
    "TierLimits",
    "QueryProfiler",
    "QueryStats",
    "get_profiler",
    "profile_query",
    "TTLCache",
    "cached",
]
