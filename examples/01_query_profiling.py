"""
Query Profiling Examples

Demonstrates how to use QueryProfiler for database query performance tracking.
"""

import asyncio
import logging
import time
from socratic_performance import QueryProfiler, get_profiler, profile_query

# Configure logging to see profiler output
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def example_decorator_profiler():
    """Example 1: Using the @profile decorator with a profiler instance."""
    print("\n=== Example 1: Decorator with Instance Profiler ===\n")
    
    profiler = QueryProfiler(slow_query_threshold_ms=50)
    
    @profiler.profile("fetch_users")
    def fetch_users(count: int) -> list:
        """Simulate a database query."""
        time.sleep(0.03)  # Simulate 30ms query
        return [f"user_{i}" for i in range(count)]
    
    @profiler.profile("fetch_posts", slow_query_threshold_ms=100)
    def fetch_posts(count: int) -> list:
        """Simulate a slower database query with custom threshold."""
        time.sleep(0.08)  # Simulate 80ms query
        return [f"post_{i}" for i in range(count)]
    
    # Call the functions
    users = fetch_users(100)
    print(f"Fetched {len(users)} users")
    
    posts = fetch_posts(50)
    print(f"Fetched {len(posts)} posts")
    
    # Get statistics
    stats = profiler.get_stats()
    print("\nCollected Statistics:")
    for name, metrics in stats.items():
        print(f"  {name}:")
        print(f"    - Count: {metrics['count']}")
        print(f"    - Avg Time: {metrics['avg_time_ms']:.2f}ms")


async def example_async_profiler():
    """Example 2: Profiling async functions."""
    print("\n=== Example 2: Async Function Profiling ===\n")
    
    profiler = QueryProfiler(slow_query_threshold_ms=100)
    
    @profiler.profile("async_query")
    async def async_database_query(query_id: str) -> dict:
        """Simulate an async database query."""
        await asyncio.sleep(0.05)  # Simulate 50ms query
        return {"id": query_id, "status": "success"}
    
    # Run multiple async queries
    results = await asyncio.gather(
        async_database_query("query_1"),
        async_database_query("query_2"),
        async_database_query("query_3"),
    )
    
    print(f"Completed {len(results)} async queries")


def example_manual_tracking():
    """Example 3: Manually tracking operations without decorator."""
    print("\n=== Example 3: Manual Tracking ===\n")
    
    profiler = QueryProfiler(slow_query_threshold_ms=100)
    
    # Simulate a complex operation with manual tracking
    start = time.time()
    time.sleep(0.12)  # Simulate 120ms operation
    duration = time.time() - start
    profiler.manual_track("complex_operation", duration, is_slow=True)
    print(f"Complex operation completed in {duration*1000:.2f}ms")
    
    # Another manual tracking example
    for i in range(3):
        start = time.time()
        time.sleep(0.02)
        duration = time.time() - start
        profiler.manual_track("loop_operation", duration)
    
    # Display results
    stats = profiler.get_stats()
    print("\nManual Tracking Statistics:")
    for name, metrics in stats.items():
        print(f"  {name}: {metrics['count']} executions")


def example_global_profiler():
    """Example 4: Using the global profiler with @profile_query decorator."""
    print("\n=== Example 4: Global Profiler ===\n")
    
    @profile_query("global_operation")
    def global_operation(data: str) -> str:
        """Operation using global profiler."""
        time.sleep(0.04)
        return f"Processed: {data}"
    
    # Execute the function
    result = global_operation("test_data")
    print(f"Result: {result}")
    
    # Get stats from global profiler
    global_profiler = get_profiler()
    stats = global_profiler.get_stats()
    print(f"\nGlobal Profiler - queries tracked: {len(stats)}")


if __name__ == "__main__":
    example_decorator_profiler()
    asyncio.run(example_async_profiler())
    example_manual_tracking()
    example_global_profiler()
    
    print("\nAll examples completed!")
