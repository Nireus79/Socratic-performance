"""Tests for performance caching modules."""

import time
import pytest
from socratic_performance import TTLCache, cached


class TestTTLCache:
    """Test cases for TTL caching functionality."""

    def test_cache_basic_functionality(self):
        """Test basic caching works and returns cached results."""
        call_count = [0]

        @cached(ttl_minutes=5)
        def expensive_function(x):
            call_count[0] += 1
            return x * 2

        # First call should execute function
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count[0] == 1

        # Second call with same args should return cached result
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count[0] == 1  # Function not called again

    def test_cache_different_args(self):
        """Test cache handles different arguments separately."""
        call_count = [0]

        @cached(ttl_minutes=5)
        def add(x, y):
            call_count[0] += 1
            return x + y

        result1 = add(1, 2)
        assert result1 == 3
        assert call_count[0] == 1

        # Different args should not use cache
        result2 = add(2, 3)
        assert result2 == 5
        assert call_count[0] == 2

        # Same args as first call should use cache
        result3 = add(1, 2)
        assert result3 == 3
        assert call_count[0] == 2

    def test_cache_with_kwargs(self):
        """Test caching works with keyword arguments."""
        call_count = [0]

        @cached(ttl_minutes=5)
        def greet(name, greeting="Hello"):
            call_count[0] += 1
            return f"{greeting}, {name}!"

        result1 = greet("Alice", greeting="Hi")
        assert result1 == "Hi, Alice!"
        assert call_count[0] == 1

        # Same call should use cache
        result2 = greet("Alice", greeting="Hi")
        assert result2 == "Hi, Alice!"
        assert call_count[0] == 1

        # Different greeting should not use cache
        result3 = greet("Alice", greeting="Hey")
        assert result3 == "Hey, Alice!"
        assert call_count[0] == 2

    def test_cache_expiration(self):
        """Test cache entries expire after TTL."""
        call_count = [0]

        @cached(ttl_minutes=0.0167)  # ~1 second
        def get_time():
            call_count[0] += 1
            return time.time()

        result1 = get_time()
        assert call_count[0] == 1

        # Immediate second call uses cache
        result2 = get_time()
        assert result1 == result2
        assert call_count[0] == 1

        # Wait for expiration
        time.sleep(1.1)

        # Should be a cache miss after expiration
        result3 = get_time()
        assert result3 > result1  # New time
        assert call_count[0] == 2

    def test_cache_clear(self):
        """Test cache_clear method removes all entries."""
        call_count = [0]

        @cached(ttl_minutes=5)
        def double(x):
            call_count[0] += 1
            return x * 2

        # Call and cache
        result1 = double(5)
        assert call_count[0] == 1

        # Use cache
        result2 = double(5)
        assert call_count[0] == 1

        # Clear cache
        double.cache_clear()

        # Should execute again
        result3 = double(5)
        assert call_count[0] == 2

    def test_cache_stats(self):
        """Test cache statistics tracking."""

        @cached(ttl_minutes=5)
        def square(x):
            return x**2

        # Generate some hits and misses
        square(1)  # miss
        square(2)  # miss
        square(1)  # hit
        square(2)  # hit
        square(3)  # miss

        stats = square.cache_stats()
        assert stats["hits"] == 2
        assert stats["misses"] == 3
        assert "hit_rate" in stats

    def test_cache_unhashable_args(self):
        """Test function with unhashable arguments raises TypeError."""

        @cached(ttl_minutes=5)
        def process_list(items):
            return sum(items)

        # List is unhashable and should raise TypeError
        # This is current behavior - could be improved to gracefully skip cache
        with pytest.raises(TypeError):
            process_list([1, 2, 3])

    def test_cache_with_none_result(self):
        """Test caching of None return values."""
        call_count = [0]

        @cached(ttl_minutes=5)
        def return_none(x):
            call_count[0] += 1
            return None if x == 0 else x

        result1 = return_none(0)
        assert result1 is None
        assert call_count[0] == 1

        # Should use cache
        result2 = return_none(0)
        assert result2 is None
        assert call_count[0] == 1

    def test_cache_exception_not_cached(self):
        """Test exceptions are not cached."""
        call_count = [0]

        @cached(ttl_minutes=5)
        def may_fail(x):
            call_count[0] += 1
            if x == 0:
                raise ValueError("Cannot process 0")
            return x * 2

        # Should raise
        with pytest.raises(ValueError):
            may_fail(0)
        assert call_count[0] == 1

        # Should call again (exception not cached)
        with pytest.raises(ValueError):
            may_fail(0)
        assert call_count[0] == 2

    def test_cache_custom_ttl(self):
        """Test custom TTL configuration."""
        cache = TTLCache(ttl_minutes=10)
        assert cache._ttl.total_seconds() == 600

    def test_ttl_cache_thread_safety(self):
        """Test cache is thread-safe."""
        import threading

        @cached(ttl_minutes=5)
        def counter(x):
            return x

        results = []

        def worker():
            for i in range(10):
                results.append(counter(i))

        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 50


class TestQueryProfiler:
    """Test cases for query profiling functionality."""

    def test_profiler_basic(self):
        """Test basic query profiling."""
        from socratic_performance import QueryProfiler

        profiler = QueryProfiler()

        @profiler.profile
        def db_query():
            return "result"

        result = db_query()
        assert result == "result"
        assert len(profiler.queries) == 1
        assert profiler.queries[0]["function"] == "db_query"

    def test_profiler_timing(self):
        """Test profiler records execution time."""
        from socratic_performance import QueryProfiler

        profiler = QueryProfiler()

        @profiler.profile
        def slow_function():
            time.sleep(0.01)  # 10ms
            return "done"

        slow_function()
        assert len(profiler.queries) == 1
        assert profiler.queries[0]["elapsed_ms"] >= 10

    def test_profiler_statistics(self):
        """Test profiler statistics calculation."""
        from socratic_performance import QueryProfiler

        profiler = QueryProfiler()

        @profiler.profile
        def test_query():
            time.sleep(0.001)
            return "result"

        # Run multiple times
        for _ in range(3):
            test_query()

        stats = profiler.get_stats()
        assert stats["total"] == 3
        assert "avg_ms" in stats
        assert stats["avg_ms"] > 0

    def test_profiler_slow_query_warning(self, caplog):
        """Test profiler logs slow queries."""
        from socratic_performance import QueryProfiler
        import logging

        caplog.set_level(logging.WARNING)
        profiler = QueryProfiler()

        @profiler.profile
        def slow():
            time.sleep(0.15)  # 150ms, exceeds threshold
            return "done"

        slow()
        assert any("Slow query" in record.message for record in caplog.records)

    def test_profiler_reset(self):
        """Test profiler reset clears data."""
        from socratic_performance import QueryProfiler

        profiler = QueryProfiler()

        @profiler.profile
        def query():
            return "result"

        query()
        assert len(profiler.queries) == 1

        profiler.reset()
        assert len(profiler.queries) == 0

    def test_profiler_empty_stats(self):
        """Test profiler stats with no queries."""
        from socratic_performance import QueryProfiler

        profiler = QueryProfiler()
        stats = profiler.get_stats()
        assert stats["total"] == 0
        assert stats["avg_ms"] == 0.0
        assert stats["slowest_queries"] == []

    def test_profiler_slowest_queries(self):
        """Test profiler identifies slowest queries."""
        from socratic_performance import QueryProfiler

        profiler = QueryProfiler()

        @profiler.profile
        def fast():
            time.sleep(0.001)
            return "fast"

        @profiler.profile
        def slow():
            time.sleep(0.05)
            return "slow"

        # Mix fast and slow queries
        for _ in range(3):
            fast()
        slow()
        for _ in range(2):
            fast()

        stats = profiler.get_stats()
        assert len(stats["slowest_queries"]) <= 5
        # Slowest should be the slow query
        assert stats["slowest_queries"][0]["function"] == "slow"


class TestCacheDecorator:
    """Test the cached decorator factory."""

    def test_cached_decorator_default_ttl(self):
        """Test cached decorator uses default TTL."""

        @cached()
        def func(x):
            return x

        result = func(5)
        assert result == 5

    def test_cached_decorator_custom_ttl(self):
        """Test cached decorator with custom TTL."""

        @cached(ttl_minutes=1)
        def func(x):
            return x

        result = func(5)
        assert result == 5

    def test_cached_preserves_function_name(self):
        """Test decorator preserves function metadata."""

        @cached(ttl_minutes=5)
        def my_function(x):
            """My docstring"""
            return x

        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "My docstring"
