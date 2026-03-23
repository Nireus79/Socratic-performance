# Socratic Performance

Performance monitoring and profiling utilities for the Socratic AI platform.

## Features

- **Query Profiling**: Track execution times of operations
- **TTL Caching**: Automatic cache expiration
- **Performance Metrics**: Comprehensive metrics collection
- **Slow Query Detection**: Identify performance bottlenecks
- **Cache Statistics**: Hit/miss ratios and effectiveness tracking
- **Trend Analysis**: Monitor performance over time

## Installation

```bash
pip install socratic-performance
```

## Quick Start

```python
from socratic_performance import QueryProfiler, TTLCache

# Profile operations
profiler = QueryProfiler()

@profiler.profile
def slow_operation():
    # Do work...
    return result

# Use caching
cache = TTLCache(ttl_minutes=30)

# Get cached value
value = cache.get("key")

# Set cache value
cache.set("key", "value")

# Get statistics
stats = profiler.get_stats()
cache_stats = cache.stats()
```

## Components

### QueryProfiler

Track execution times of operations.

```python
profiler = QueryProfiler()

@profiler.profile
def my_function():
    return "result"

stats = profiler.get_stats()
slow = profiler.get_slow_queries(threshold_ms=1000)
```

### TTLCache

Time-to-live based caching.

```python
cache = TTLCache(ttl_minutes=30)

cache.set("key", "value")
value = cache.get("key")
cache.cleanup_expired()
stats = cache.stats()
```

### PerformanceMetrics

Comprehensive performance metrics.

```python
from socratic_performance import PerformanceMetrics, MetricsCollector

collector = MetricsCollector()
metrics = collector.collect(
    profiler_stats=profiler.get_stats(),
    cache_stats=cache.stats()
)
```

## License

MIT
