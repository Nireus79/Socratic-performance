# socratic-performance Architecture

Performance monitoring, query profiling, and caching utilities for Socratic systems.

## System Overview

```
Application Layer
    |
    +-- Query Execution (sync/async)
    |   |
    |   +-- QueryProfiler (decorator-based)
    |   |
    |   +-- TTLCache (result caching)
    |
    +-- Metrics & Statistics
    |   |
    |   +-- Performance Tracking
    |   +-- Slow Query Detection
    |   +-- Cache Statistics
```

## Core Components

### 1. QueryProfiler

**High-level query performance tracking**:
- Decorator-based instrumentation
- Supports both sync and async functions
- Automatic execution time tracking
- Slow query detection and logging
- Performance statistics aggregation
- Global profiler instance available

**Key Classes:**
- `QueryProfiler`: Main profiler class with configurable thresholds
- `QueryStats`: Per-query statistics container
- Module functions: `get_profiler()`, `profile_query()`

**Features:**
- Tracks: count, total time, min/max time, averages
- Identifies slow executions and errors
- Generates performance summaries
- Supports manual tracking without decorator

### 2. TTLCache

**Time-based result caching with automatic expiration**:
- Thread-safe caching using RLock
- Configurable time-to-live (TTL)
- Graceful handling of unhashable arguments
- Cache statistics and hit rate tracking
- Cache management methods

**Key Classes:**
- `TTLCache`: Main cache decorator class
- Decorator factory: `cached(ttl_minutes)`

**Features:**
- Automatic cache key generation from args/kwargs
- Expired entry removal
- Hit/miss tracking
- Cache clear and reset operations

## Data Structures

### QueryStats

```python
{
    "name": str,                    # Query name
    "count": int,                   # Total executions
    "avg_time_ms": float,           # Average execution time
    "min_time_ms": float,           # Minimum execution time
    "max_time_ms": float,           # Maximum execution time
    "total_time_ms": float,         # Total execution time
    "slow_count": int,              # Number of slow executions
    "slow_percentage": float,       # Percentage that were slow
    "error_count": int,             # Number of errors
    "last_executed_at": float,      # Unix timestamp of last execution
}
```

### CacheStats

```python
{
    "hits": int,                    # Cache hits
    "misses": int,                  # Cache misses
    "total_calls": int,             # Total cache lookups
    "hit_rate": str,                # Percentage hit rate
    "cache_size": int,              # Number of cached entries
    "ttl_minutes": float,           # Time-to-live in minutes
}
```

## Execution Flow

### Query Profiling

1. **Decorator Application**
   - `@profiler.profile("query_name")`
   - Creates wrapper function
   - Initializes QueryStats if new

2. **Function Execution**
   - Record start time
   - Execute original function (sync or async)
   - Calculate duration
   - Determine if slow (duration > threshold)

3. **Statistics Update**
   - Update count, timing metrics
   - Record slow/error flags
   - Update last execution time

4. **Logging**
   - Debug: Normal executions
   - Warning: Slow queries
   - Error: Failed queries

### Cache Operations

1. **Cache Lookup**
   - Generate cache key from args/kwargs
   - Check if key exists and not expired
   - Return cached result (cache hit)
   - Or proceed to compute (cache miss)

2. **Cache Store**
   - Compute function result
   - Store in cache with timestamp
   - Update hit/miss counters

3. **Expiration**
   - Check age: `current_time - timestamp < ttl`
   - Remove expired entries on access
   - Optional manual cleanup

## Thread Safety

### QueryProfiler
- Uses internal dictionary for stats
- Dictionary operations are atomic in Python
- Safe for concurrent access from multiple threads

### TTLCache
- Uses `threading.RLock` for synchronization
- Protects cache dictionary and counters
- Computes function outside lock to avoid blocking

## Performance Characteristics

### QueryProfiler
- **Time Overhead**: ~1-2 microseconds per call (timing only)
- **Memory**: Minimal - one QueryStats object per unique query
- **Scalability**: O(1) lookups, supports thousands of tracked queries

### TTLCache
- **Time Overhead**: ~5-10 microseconds for cache lookup/store
- **Memory**: One entry per unique arguments combination
- **Scalability**: O(1) cache lookups via hash table

## Integration with Socratic

### With socratic-nexus
- Profile model invocation performance
- Identify slow API calls
- Cache model responses

### With socratic-analyzer
- Track analysis query performance
- Identify bottlenecks in analysis pipelines

### With socratic-knowledge
- Profile knowledge base queries
- Cache knowledge lookups

### With Socrates (main)
- Extract performance metrics for reporting
- Monitor query performance across ecosystem

## Configuration

### QueryProfiler Configuration

```python
profiler = QueryProfiler(
    slow_query_threshold_ms=100.0  # Customize per use case
)

# Or override per query
@profiler.profile("fast_query", slow_query_threshold_ms=50)
def fast_operation():
    pass
```

### TTLCache Configuration

```python
cache = TTLCache(ttl_minutes=5)       # Instance decorator
cached(ttl_minutes=10)                 # Factory function
```

## Error Handling

### QueryProfiler
- Catches exceptions during execution
- Records error in statistics
- Logs error with duration
- Re-raises exception

### TTLCache
- Gracefully skips caching for unhashable arguments
- Logs warnings for skipped cache operations
- Returns function result without caching

## Usage Patterns

### Pattern 1: Query Monitoring
```python
profiler = QueryProfiler()

@profiler.profile("slow_check")
async def check_something():
    pass

# Monitor over time
stats = profiler.get_stats()
```

### Pattern 2: Result Caching
```python
@cached(ttl_minutes=5)
def expensive_operation(param):
    return compute(param)

# Automatic caching and expiration
result = expensive_operation("key")
```

### Pattern 3: Combined
```python
profiler = QueryProfiler()
cache = TTLCache()

@cache
@profiler.profile("operation")
def my_operation(x):
    return compute(x)

# Profile execution time, cache results
```

## Monitoring & Debugging

### Query Profiling
- `profiler.print_summary()` - Print performance report
- `profiler.get_slow_queries()` - Find problematic queries
- `profiler.get_slowest_queries()` - Identify bottlenecks
- `profiler.get_stats()` - Raw statistics

### Cache Monitoring
- `function.cache_stats()` - Hit/miss rates
- `function.cache_info()` - Human-readable cache status
- `function.cache_clear()` - Clear cache when needed

## Future Enhancements

1. **Metrics Export**
   - Prometheus metrics format
   - OpenTelemetry integration

2. **Advanced Caching**
   - Distributed cache support
   - Cache warming strategies
   - Eviction policies

3. **Distributed Profiling**
   - Collect metrics across services
   - Distributed tracing support
   - Aggregated dashboards

---

Part of the Socratic Ecosystem v1.3.3+
