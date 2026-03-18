# Socratic Performance

Performance monitoring and caching utilities for AI systems.

## Features

- **QueryProfiler**: Database query profiling and performance monitoring
- **TTLCache**: Time-based function result caching decorator

## Installation

```bash
pip install socratic-performance
```

## Usage

### Query Profiler

```python
from socratic_performance import QueryProfiler

profiler = QueryProfiler()

@profiler.profile
def expensive_query():
    # Your database query here
    pass

expensive_query()
stats = profiler.get_stats()
print(stats)
```

### TTL Cache

```python
from socratic_performance import cached

@cached(ttl_minutes=5)
def compute_something(x):
    return x * x

result1 = compute_something(10)  # Computed
result2 = compute_something(10)  # Cached (5 min)
```

## Documentation

- **[Performance Profiling Guide](docs/PERFORMANCE_PROFILING.md)** - Complete guide to performance profiling, query optimization, metrics collection, and bottleneck identification

## License

MIT
