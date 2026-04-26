# Socratic Performance

Performance monitoring and caching utilities for AI systems.

## Features

- **QueryProfiler**: Database query profiling and performance monitoring with support for sync and async functions
- **TTLCache**: Time-based function result caching decorator with thread-safe cache management
- **Performance Analytics**: Track slow queries, get performance summaries, and analyze bottlenecks
- **Cache Statistics**: Monitor cache hits, misses, and hit rates

## Installation

```bash
pip install socratic-performance
```

## Quick Start

### Query Profiling

Track database query performance with automatic slow query detection:

```python
from socratic_performance import QueryProfiler

profiler = QueryProfiler(slow_query_threshold_ms=100)

@profiler.profile("get_user")
async def load_user(user_id: str):
    # Your async database query here
    return await db.get(User, user_id)

# Execute the function
user = await load_user("user_123")

# Get statistics
stats = profiler.get_stats()
print(f"get_user avg time: {stats['get_user']['avg_time_ms']:.2f}ms")

# Get slowest queries
slowest = profiler.get_slowest_queries(limit=5)
for query in slowest:
    print(f"{query['name']}: {query['avg_time_ms']:.1f}ms")
```

### TTL Caching

Cache expensive function results with automatic expiration:

```python
from socratic_performance import cached

@cached(ttl_minutes=5)
def expensive_computation(project_id: str) -> dict:
    # Simulate expensive operation
    return analyze_project(project_id)

result1 = expensive_computation("proj_123")  # Computed (slow)
result2 = expensive_computation("proj_123")  # Cached (fast)

# Check cache statistics
stats = expensive_computation.cache_stats()
print(f"Cache hit rate: {stats['hit_rate']}")
```

## API Reference

### QueryProfiler

#### Initialization

```python
profiler = QueryProfiler(slow_query_threshold_ms=100.0)
```

**Parameters:**
- `slow_query_threshold_ms` (float): Threshold above which queries are considered slow (default: 100ms)

#### Decorator Usage

```python
@profiler.profile("query_name")
async def my_query():
    pass

@profiler.profile("custom_threshold", slow_query_threshold_ms=50)
def fast_query():
    pass
```

#### Manual Tracking

```python
start = time.time()
try:
    result = perform_operation()
    duration = time.time() - start
    profiler.manual_track("operation", duration)
except Exception:
    duration = time.time() - start
    profiler.manual_track("operation", duration, error=True)
    raise
```

#### Statistics Methods

```python
# Get all statistics
stats = profiler.get_stats()

# Get slow queries (with slow executions)
slow_queries = profiler.get_slow_queries(min_slow_count=1)

# Get slowest queries (by average time)
slowest = profiler.get_slowest_queries(limit=10)

# Print summary
profiler.print_summary(limit=5)

# Reset statistics
profiler.reset_stats()  # Reset all
profiler.reset_stats("specific_query")  # Reset one
```

### TTLCache

#### Decorator Usage

```python
cache = TTLCache(ttl_minutes=5)

@cache
def expensive_operation(x, y):
    return x + y
```

#### Factory Function

```python
from socratic_performance import cached

@cached(ttl_minutes=10)
def my_function(param):
    return expensive_operation(param)
```

#### Cache Management

```python
# Clear cache
my_function.cache_clear()

# Get statistics
stats = my_function.cache_stats()
# Returns: {'hits': 5, 'misses': 3, 'total_calls': 8, 'hit_rate': '62.5%', ...}

# Get human-readable info
info = my_function.cache_info()
# Returns: "Cache: 3 entries, 62.5% hit rate, TTL: 10 minutes"
```

#### TTLCache Methods

```python
cache = TTLCache(ttl_minutes=5)

# Clean up expired entries
removed_count = cache.cleanup_expired()

# Reset statistics only (keep cache)
cache.reset_stats()

# Clear all cache
cache.clear()
```

## Examples

See the `examples/` directory for complete examples:

- **[01_query_profiling.py](examples/01_query_profiling.py)** - Query profiling with decorators, manual tracking, async functions
- **[02_ttl_cache.py](examples/02_ttl_cache.py)** - TTL cache usage, multiple functions, kwargs handling

Run examples:

```bash
python examples/01_query_profiling.py
python examples/02_ttl_cache.py
```

## Global Profiler

Access a global profiler instance without managing your own:

```python
from socratic_performance import get_profiler, profile_query

@profile_query("operation_name")
async def my_operation():
    pass

# Get global profiler
profiler = get_profiler()
stats = profiler.get_stats()
```

## Best Practices

### Query Profiling

1. **Set appropriate thresholds**: Tune `slow_query_threshold_ms` based on your performance requirements
2. **Use meaningful names**: Give queries descriptive names for easy identification
3. **Review slow queries regularly**: Use `get_slow_queries()` and `get_slowest_queries()` to identify bottlenecks
4. **Print summaries**: Use `print_summary()` to log performance reports

### TTL Caching

1. **Choose appropriate TTLs**: Balance freshness vs. performance
2. **Monitor hit rates**: Check `cache_stats()` to ensure caching is effective
3. **Handle unhashable arguments**: The cache gracefully skips caching for unhashable arguments
4. **Clean up expired entries**: Call `cleanup_expired()` periodically for long-running processes

## Architecture

**QueryProfiler** provides low-overhead query performance tracking:
- Works with both sync and async functions
- Configurable slow query thresholds
- Automatic error tracking
- Minimal performance impact

**TTLCache** implements thread-safe result caching:
- Automatic expiration after TTL
- Thread-safe operations using RLock
- Graceful handling of unhashable arguments
- Detailed cache statistics

## License

MIT

## Contributing

Contributions welcome! Please ensure tests pass and code is formatted with black.

```bash
pytest tests/
black .
```
