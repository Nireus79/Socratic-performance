"""
TTL Cache Examples

Demonstrates how to use TTLCache for function result caching with time-to-live.
"""

import logging
import time
from socratic_performance import TTLCache, cached

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def example_basic_ttl_cache():
    """Example 1: Basic TTLCache usage as a decorator."""
    print("\n=== Example 1: Basic TTLCache Decorator ===\n")
    
    cache = TTLCache(ttl_minutes=1)
    
    @cache
    def expensive_computation(x: int, y: int) -> int:
        """Simulate an expensive computation."""
        print(f"  Computing {x} + {y}...")
        time.sleep(0.5)  # Simulate slow operation
        return x + y
    
    # First call - computes result
    print("First call:")
    result1 = expensive_computation(5, 3)
    print(f"  Result: {result1}")
    
    # Second call - should use cache
    print("\nSecond call (should be cached):")
    result2 = expensive_computation(5, 3)
    print(f"  Result: {result2}")
    
    # Different arguments - should compute again
    print("\nThird call (different args):")
    result3 = expensive_computation(10, 20)
    print(f"  Result: {result3}")
    
    # Check cache stats
    stats = expensive_computation.cache_stats()
    print(f"\nCache Statistics: {stats}")


def example_cached_factory():
    """Example 2: Using the @cached() decorator factory."""
    print("\n=== Example 2: Using @cached() Factory ===\n")
    
    @cached(ttl_minutes=2)
    def api_call(endpoint: str, param: str) -> dict:
        """Simulate an API call."""
        print(f"  Making API call to {endpoint} with {param}...")
        time.sleep(0.3)
        return {"endpoint": endpoint, "param": param, "status": "success"}
    
    # Multiple API calls with some repeated
    calls = [
        ("users", "123"),
        ("users", "123"),  # Cache hit
        ("posts", "456"),
        ("users", "123"),  # Cache hit
    ]
    
    for endpoint, param in calls:
        print(f"\nCalling: {endpoint} / {param}")
        result = api_call(endpoint, param)
        print(f"  Status: {result['status']}")
    
    # Show cache info
    print(f"\nCache Info: {api_call.cache_info()}")


def example_multiple_cached():
    """Example 3: Multiple functions with different TTL values."""
    print("\n=== Example 3: Multiple Cached Functions ===\n")
    
    @cached(ttl_minutes=1)
    def get_user_data(user_id: int) -> dict:
        """Get user data (short TTL)."""
        print(f"  Fetching user {user_id}...")
        time.sleep(0.2)
        return {"user_id": user_id, "name": f"User{user_id}"}
    
    @cached(ttl_minutes=10)
    def get_configuration() -> dict:
        """Get configuration (longer TTL)."""
        print(f"  Loading configuration...")
        time.sleep(0.3)
        return {"setting1": "value1", "setting2": "value2"}
    
    # Use both functions
    print("First calls (all computed):")
    user = get_user_data(1)
    config = get_configuration()
    print(f"  User: {user['name']}")
    print(f"  Config loaded: {len(config)} settings")
    
    print("\nSecond calls (should be cached):")
    user = get_user_data(1)
    config = get_configuration()
    print(f"  User: {user['name']}")
    print(f"  Config loaded: {len(config)} settings")
    
    print(f"\nUser cache hits/misses: {get_user_data.cache_stats()['hit_rate']}")
    print(f"Config cache hits/misses: {get_configuration.cache_stats()['hit_rate']}")


def example_cache_clearing():
    """Example 4: Clearing cache."""
    print("\n=== Example 4: Cache Clearing ===\n")
    
    @cached(ttl_minutes=5)
    def calculate(x: int) -> int:
        print(f"  Calculating {x}^2...")
        time.sleep(0.1)
        return x * x
    
    # Cache a result
    print("First call:")
    result1 = calculate(5)
    print(f"  Result: {result1}")
    stats1 = calculate.cache_stats()
    print(f"  Cache size: {stats1['cache_size']}")
    
    # Clear cache
    print("\nClearing cache...")
    calculate.cache_clear()
    stats2 = calculate.cache_stats()
    print(f"  Cache size after clear: {stats2['cache_size']}")


def example_kwargs_caching():
    """Example 5: Caching with keyword arguments."""
    print("\n=== Example 5: Keyword Arguments Caching ===\n")
    
    @cached(ttl_minutes=5)
    def database_query(query: str, limit: int = 10) -> list:
        """Simulate database query with kwargs."""
        print(f"  Querying: {query} (limit={limit})...")
        time.sleep(0.2)
        return [f"result_{i}" for i in range(limit)]
    
    # Test various call combinations
    print("First call with limit=10:")
    result = database_query("SELECT * FROM users")
    print(f"  Got {len(result)} results")
    
    print("\nSecond call with limit=20:")
    result = database_query("SELECT * FROM users", limit=20)
    print(f"  Got {len(result)} results")
    
    print("\nThird call with limit=10 (should be cached):")
    result = database_query("SELECT * FROM users")
    print(f"  Got {len(result)} results")
    
    stats = database_query.cache_stats()
    print(f"\nFinal cache stats: {stats}")


if __name__ == "__main__":
    example_basic_ttl_cache()
    example_cached_factory()
    example_multiple_cached()
    example_cache_clearing()
    example_kwargs_caching()
    
    print("\n\nAll TTL cache examples completed!")
