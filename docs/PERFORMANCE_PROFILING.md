# Performance Profiling and Monitoring - Complete Technical Documentation

**Version:** 1.0
**Last Updated:** March 2026
**Scope:** socratic-performance - System Performance Optimization Tools

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Query Profiler](#query-profiler)
4. [TTL Function Cache](#ttl-function-cache)
5. [Metrics Collection](#metrics-collection)
6. [Performance Analysis](#performance-analysis)
7. [Best Practices](#best-practices)
8. [Integration Guide](#integration-guide)
9. [API Reference](#api-reference)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The **socratic-performance** module provides production-grade performance profiling and optimization tools for Socrates AI systems. It enables developers to:

### Key Capabilities

- **Database Query Profiling**: Identify slow queries and optimization opportunities
- **Function Result Caching**: Automatic memoization with TTL-based expiration
- **Metrics Collection**: Track execution times, memory usage, and throughput
- **Performance Bottleneck Detection**: Find and prioritize optimization targets
- **Transparent Integration**: Drop-in decorators for profiling and caching
- **Observable Systems**: Detailed logging and statistics for monitoring

### Quick Start

```python
from socratic_performance.profiling import profile_query
from socratic_performance.caching import ttl_cache

# Profile database queries
@profile_query
def get_user_projects(user_id):
    return db.query("SELECT * FROM projects WHERE user_id = ?", user_id)

# Cache expensive function results with 5-minute TTL
@ttl_cache(ttl_seconds=300)
def calculate_maturity_metrics(project_id):
    return expensive_calculation(project_id)

# Use as normal
projects = get_user_projects(user_id="123")
metrics = calculate_maturity_metrics(project_id="456")

# Access profiling data
profiling_stats = get_user_projects.stats()
cache_stats = calculate_maturity_metrics.cache_stats()
```

---

## Architecture

### System Components

```
Application Code
│
├── Profiled Functions
│   ├── @profile_query
│   │   └── Query Profiler
│   │       ├── Timing measurement
│   │       ├── Row count tracking
│   │       └── Query fingerprinting
│   │
│   └── @ttl_cache
│       └── TTL Cache
│           ├── Result memoization
│           ├── Expiration tracking
│           └── Hit/miss statistics
│
└── Performance Metrics
    ├── Execution times (min, max, avg)
    ├── Query patterns
    ├── Cache effectiveness
    └── System bottlenecks
```

### Design Philosophy

1. **Zero-Overhead in Fast Path**: Minimal performance impact on normal operations
2. **Decorator-Based**: Non-intrusive integration with existing code
3. **Observable**: All metrics exposed for monitoring and debugging
4. **Thread-Safe**: Safe for concurrent access in multi-threaded applications
5. **Production-Ready**: Robust error handling and resource management

---

## Query Profiler

### Purpose

The Query Profiler captures performance metrics for database queries, helping identify:
- Slow queries that need optimization
- Unexpected query patterns
- N+1 query problems
- Inefficient data access patterns

### Implementation Details

**Tracked Metrics**:
```python
{
    "query_fingerprint": str,      # Normalized query for grouping
    "execution_count": int,        # How many times executed
    "total_time": float,           # Total execution time (seconds)
    "avg_time": float,             # Average execution time
    "min_time": float,             # Minimum execution time
    "max_time": float,             # Maximum execution time
    "total_rows": int,             # Total rows returned
    "avg_rows": float,             # Average rows per execution
    "last_executed": datetime,     # Most recent execution
}
```

### Usage

```python
from socratic_performance.profiling import profile_query

# Automatic profiling decorator
@profile_query
def get_project_details(project_id):
    """Get comprehensive project information."""
    return db.execute("""
        SELECT p.*, COUNT(t.id) as task_count
        FROM projects p
        LEFT JOIN tasks t ON p.id = t.project_id
        WHERE p.id = ?
        GROUP BY p.id
    """, project_id)

# Use normally
project = get_project_details(project_id="123")

# Get statistics
stats = get_project_details.stats()
print(f"Avg execution time: {stats['avg_time']*1000:.2f}ms")
print(f"Total rows: {stats['total_rows']}")
```

### Query Fingerprinting

The profiler normalizes queries to group similar patterns:

```python
# These queries are grouped together
SELECT * FROM users WHERE id = 1
SELECT * FROM users WHERE id = 2
SELECT * FROM users WHERE id = 3

# Fingerprint: SELECT * FROM users WHERE id = ?
```

This enables identifying N+1 query problems:

```python
# Anti-pattern: N+1 queries
@profile_query
def get_user_with_projects(user_id):
    user = db.query("SELECT * FROM users WHERE id = ?", user_id)
    projects = db.query("SELECT * FROM projects WHERE user_id = ?", user_id)
    return {user, projects}

# Problem identified: Inner query runs N times (once per user)
# Solution: Use JOIN or batch query
```

### Performance Analysis API

```python
def analyze_queries():
    """Analyze all profiled queries."""
    stats = get_project_details.stats()

    # Identify slow queries
    if stats['avg_time'] > 0.1:  # 100ms threshold
        logger.warning(f"Slow query: {stats['query_fingerprint']}")

    # Check execution count
    if stats['execution_count'] > 100:
        logger.info(f"Frequently executed: {stats['query_fingerprint']}")

    return stats
```

---

## TTL Function Cache

### Purpose

The TTL (Time-To-Live) Function Cache memoizes expensive function results with automatic expiration. Valuable for:

- Computational calculations (maturity scoring, metrics)
- API calls to external services
- Complex data transformations
- Frequently accessed data that changes infrequently

### Implementation Details

**Cache Structure**:
```python
{
    "function_args_hash": (
        result,
        expiration_time
    ),
    ...
}
```

**Key Features**:
- Automatic TTL-based expiration
- Thread-safe concurrent access
- Configurable TTL per function
- Hit/miss statistics
- Optional argument serialization

### Usage

```python
from socratic_performance.caching import ttl_cache

# 5-minute cache for expensive calculation
@ttl_cache(ttl_seconds=300)
def calculate_maturity_score(project_id):
    """Calculate project maturity (expensive operation)."""
    # ... complex calculation ...
    return maturity_score

# 1-hour cache for stable reference data
@ttl_cache(ttl_seconds=3600)
def get_category_definitions():
    """Get maturity categories (rarely changes)."""
    return load_categories_from_db()

# Use normally - caching is transparent
score = calculate_maturity_score(project_id="123")
categories = get_category_definitions()

# Check cache effectiveness
cache_stats = calculate_maturity_score.cache_stats()
print(f"Cache hit rate: {cache_stats['hit_rate']}")
```

### Cache Key Generation

By default, cache keys are generated from function arguments:

```python
@ttl_cache(ttl_seconds=300)
def process_data(project_id, user_id, analysis_type="full"):
    return analyze(project_id, user_id, analysis_type)

# Different cache entries for different arguments
process_data("proj_1", "user_1")  # Cache key 1
process_data("proj_1", "user_2")  # Cache key 2 (different user)
process_data("proj_2", "user_1")  # Cache key 3 (different project)
process_data("proj_1", "user_1")  # Hits cache key 1
```

### TTL Selection Guidelines

| Duration | Use Case | Example |
|----------|----------|---------|
| **30-60 sec** | Real-time calculations | User interaction logging |
| **5 min** | Frequently requested data | Project maturity scores |
| **15-30 min** | Semi-stable data | Category definitions |
| **1+ hour** | Reference data | Skill definitions |

### Memory Management

```python
# Default configuration balances hit rate and memory
@ttl_cache(ttl_seconds=300)  # 5 minutes
def moderate_cache(arg):
    return expensive_calc(arg)

# For large result objects, use shorter TTL
@ttl_cache(ttl_seconds=60)  # 1 minute
def lightweight_cache(arg):
    return expensive_calc(arg)

# For small results, can use longer TTL
@ttl_cache(ttl_seconds=3600)  # 1 hour
def persistent_cache(arg):
    return expensive_calc(arg)
```

### Cache Invalidation

```python
# Manual invalidation (when data changes)
@ttl_cache(ttl_seconds=300)
def get_project_data(project_id):
    return fetch_from_db(project_id)

# Clear cache for specific arguments
get_project_data.invalidate(project_id="123")

# Clear entire function cache
get_project_data.clear_cache()
```

---

## Metrics Collection

### Available Metrics

**Query Profiler Metrics**:
```python
{
    "query_fingerprint": str,
    "execution_count": int,
    "total_time": float,
    "avg_time": float,
    "min_time": float,
    "max_time": float,
    "total_rows": int,
    "avg_rows": float,
    "last_executed": datetime,
}
```

**TTL Cache Metrics**:
```python
{
    "hits": int,
    "misses": int,
    "total_calls": int,
    "hit_rate": float,
    "cache_size": int,
    "ttl_seconds": int,
    "last_access": datetime,
}
```

### Accessing Metrics

```python
# Query profiler stats
query_stats = get_project_details.stats()
print(f"Query executed {query_stats['execution_count']} times")
print(f"Average time: {query_stats['avg_time']*1000:.2f}ms")

# Cache stats
cache_stats = calculate_maturity.cache_stats()
print(f"Cache hit rate: {cache_stats['hit_rate']*100:.1f}%")
print(f"Items in cache: {cache_stats['cache_size']}")
```

### Exporting Metrics

```python
import json
from datetime import datetime

def export_performance_metrics(functions):
    """Export all performance metrics to JSON."""
    metrics = {}

    for func in functions:
        if hasattr(func, 'stats'):
            metrics[func.__name__] = {
                "type": "query_profiler",
                "stats": func.stats(),
            }
        elif hasattr(func, 'cache_stats'):
            metrics[func.__name__] = {
                "type": "ttl_cache",
                "stats": func.cache_stats(),
            }

    return json.dumps(metrics, default=str, indent=2)

# Export metrics
report = export_performance_metrics([
    get_project_details,
    calculate_maturity_score,
])
print(report)
```

---

## Performance Analysis

### Identifying Bottlenecks

**1. Slow Query Detection**:
```python
def find_slow_queries(threshold_ms=100):
    """Find queries exceeding threshold."""
    slow_queries = []

    for func in monitored_functions:
        if hasattr(func, 'stats'):
            stats = func.stats()
            if stats['avg_time'] * 1000 > threshold_ms:
                slow_queries.append({
                    'query': stats['query_fingerprint'],
                    'avg_time_ms': stats['avg_time'] * 1000,
                    'executions': stats['execution_count'],
                })

    return slow_queries
```

**2. N+1 Query Detection**:
```python
def find_n_plus_one_queries():
    """Identify patterns suggesting N+1 queries."""
    patterns = {}

    for func in monitored_functions:
        if hasattr(func, 'stats'):
            stats = func.stats()
            fingerprint = stats['query_fingerprint']

            # If same query runs many times, it might be N+1
            if stats['execution_count'] > 10:
                patterns[fingerprint] = stats['execution_count']

    return patterns
```

**3. Cache Effectiveness**:
```python
def analyze_cache_effectiveness():
    """Analyze which caches are most effective."""
    effective = []

    for func in cached_functions:
        stats = func.cache_stats()
        hit_rate = stats['hit_rate']

        if hit_rate > 0.5:  # >50% hit rate is good
            effective.append({
                'function': func.__name__,
                'hit_rate': hit_rate,
                'calls_saved': stats['hits'],
            })

    return effective
```

### Creating Performance Reports

```python
def generate_performance_report():
    """Generate comprehensive performance report."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "slow_queries": find_slow_queries(threshold_ms=100),
        "n_plus_one_patterns": find_n_plus_one_queries(),
        "cache_effectiveness": analyze_cache_effectiveness(),
        "recommendations": [],
    }

    # Generate recommendations
    if report['slow_queries']:
        report['recommendations'].append(
            "Consider optimizing or indexing slow queries"
        )

    if report['n_plus_one_patterns']:
        report['recommendations'].append(
            "Investigate N+1 query patterns"
        )

    return report
```

---

## Best Practices

### 1. Profile Critical Paths

```python
# Good: Profile hot paths
@profile_query
def get_user_projects(user_id):
    """Frequently called - profile it."""
    return db.query(...)

# Avoid: Profiling rarely-called functions
@profile_query
def initialize_system():
    """Called once - no need to profile."""
    return setup()
```

### 2. Use Appropriate Cache TTL

```python
# Good: Short TTL for data that changes frequently
@ttl_cache(ttl_seconds=60)
def get_active_sessions():
    return db.query("SELECT * FROM sessions WHERE active")

# Bad: Long TTL for data that changes frequently
@ttl_cache(ttl_seconds=3600)
def get_active_sessions():
    return db.query("SELECT * FROM sessions WHERE active")
```

### 3. Monitor Cache Hit Rates

```python
# Regularly check cache effectiveness
def monitor_caches():
    for func in cached_functions:
        stats = func.cache_stats()
        if stats['hit_rate'] < 0.2:
            logger.warning(
                f"{func.__name__} has low hit rate: {stats['hit_rate']}"
            )
```

### 4. Set Profiling Thresholds

```python
# Profile only expensive operations
import time

def profile_if_slow(threshold_ms=10):
    """Decorator that only enables profiling for slow operations."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = (time.time() - start) * 1000

            if elapsed > threshold_ms:
                logger.info(f"{func.__name__} took {elapsed:.2f}ms")

            return result
        return wrapper
    return decorator
```

### 5. Clean Up Resources

```python
def cleanup_performance_metrics():
    """Clear old metrics to prevent memory growth."""
    for func in monitored_functions:
        if hasattr(func, 'clear_cache'):
            func.clear_cache()

# Call on shutdown
import atexit
atexit.register(cleanup_performance_metrics)
```

---

## Integration Guide

### With Socrates API

```python
from fastapi import FastAPI
from socratic_performance.profiling import profile_query
from socratic_performance.caching import ttl_cache

app = FastAPI()

# Cache expensive calculations
@ttl_cache(ttl_seconds=300)
def get_maturity_metrics(project_id):
    """Calculate maturity - cached for 5 minutes."""
    return calculate_maturity(project_id)

# Profile database queries
@profile_query
def fetch_project(project_id):
    """Fetch project with profiling."""
    return db.query("SELECT * FROM projects WHERE id = ?", project_id)

@app.get("/projects/{project_id}/metrics")
def get_metrics(project_id: str):
    """API endpoint with automatic caching and profiling."""
    project = fetch_project(project_id)
    metrics = get_maturity_metrics(project_id)

    return {
        "project": project,
        "metrics": metrics,
        "profiling": fetch_project.stats(),
        "cache_stats": get_maturity_metrics.cache_stats(),
    }
```

### With Socratic Learning System

```python
from socratic_learning import InteractionLogger
from socratic_performance.caching import ttl_cache

# Cache learning recommendations
@ttl_cache(ttl_seconds=600)  # 10-minute cache
def generate_learning_recommendations(user_id, project_id):
    """Generate personalized recommendations."""
    logger = InteractionLogger()
    history = logger.get_interaction_history(user_id, project_id)
    return recommend(history)

# Use in agent
recommendations = generate_learning_recommendations(
    user_id="user_123",
    project_id="proj_456"
)
```

### With Custom Applications

```python
from socratic_performance.profiling import profile_query
from socratic_performance.caching import ttl_cache

class PerformanceOptimizedService:
    """Service with built-in performance monitoring."""

    @profile_query
    def expensive_operation(self, data):
        """This operation is profiled."""
        return process(data)

    @ttl_cache(ttl_seconds=300)
    def cached_calculation(self, param):
        """Result is cached for 5 minutes."""
        return calculate(param)

    def get_performance_report(self):
        """Get performance metrics."""
        return {
            "operation_stats": self.expensive_operation.stats(),
            "cache_stats": self.cached_calculation.cache_stats(),
        }
```

---

## API Reference

### profile_query Decorator

```python
@profile_query
def function(args) -> Any:
    """Decorator that profiles function execution.

    Tracks:
    - Execution time (min, max, avg)
    - Execution count
    - Row count (for database queries)
    - Query fingerprint

    Accessible via:
    - function.stats() -> Dict[str, Any]
    """
```

### ttl_cache Decorator

```python
@ttl_cache(ttl_seconds=300)
def function(args) -> Any:
    """Decorator that caches result with TTL.

    Args:
        ttl_seconds: Time-to-live in seconds

    Accessible via:
    - function.cache_stats() -> Dict[str, Any]
    - function.invalidate(*args, **kwargs) -> None
    - function.clear_cache() -> None
    """
```

### Utility Functions

```python
def export_metrics(functions: List) -> Dict:
    """Export metrics from multiple functions."""

def generate_report(functions: List) -> Dict:
    """Generate comprehensive performance report."""

def find_bottlenecks(functions: List, threshold: float) -> List:
    """Identify slow functions."""
```

---

## Troubleshooting

### Low Cache Hit Rate

**Symptoms**: Cache statistics show <20% hit rate

**Solutions**:
1. Verify arguments are identical (object equality)
2. Increase TTL if data is changing frequently
3. Check if function is being called with many unique argument combinations
4. Review cache invalidation logic

```python
# Debug: Check what arguments are being cached
@ttl_cache(ttl_seconds=300)
def debug_cache(arg):
    print(f"Cache call with arg: {arg}")
    return expensive_calc(arg)
```

### High Memory Usage from Cache

**Symptoms**: Memory grows significantly with TTL cache

**Solutions**:
1. Reduce TTL to expire results sooner
2. Reduce number of cached functions
3. Clear cache periodically
4. Use query profiler to identify if caching is necessary

```python
# Memory-conscious configuration
@ttl_cache(ttl_seconds=60)  # Short TTL
def light_cache(arg):
    return calc(arg)

# Clear regularly
import threading
def clear_old_caches():
    light_cache.clear_cache()

timer = threading.Timer(300, clear_old_caches)
timer.start()
```

### Profiler Overhead

**Symptoms**: Profiling adds noticeable latency

**Solutions**:
1. Profile only hot paths, not every function
2. Use lightweight profiling (sample-based)
3. Disable profiling in production if needed
4. Use conditional profiling based on performance thresholds

```python
# Only profile if function is slow
import time
import os

PROFILE_ENABLED = os.getenv("PROFILE_ENABLED", "false").lower() == "true"

def conditional_profile(func):
    if PROFILE_ENABLED:
        return profile_query(func)
    return func
```

---

## Summary

The socratic-performance module provides:

- **Query Profiler**: Identify and optimize database performance
- **TTL Cache**: Automatic result memoization with expiration
- **Metrics Collection**: Observable performance data
- **Bottleneck Detection**: Find optimization opportunities
- **Production-Ready**: Transparent, thread-safe integration

Enable it with minimal code changes to gain deep insights into system performance and optimize critical paths.
