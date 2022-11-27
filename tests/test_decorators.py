from django.core.cache import cache
from django.test import SimpleTestCase

from ormcache.decorators import cache_result


class DecoratorsCacheTestCase(SimpleTestCase):
    def test_cache_result(self):
        call_counts = [0]
        value = {"hello": "world"}

        @cache_result()
        def random_function():
            call_counts[0] += 1
            return value

        result = random_function()
        self.assertTrue(value, result)
        self.assertEqual(1, call_counts[0])

        result = random_function()
        self.assertTrue(value, result)
        self.assertEqual(1, call_counts[0])

        cache.clear()
        result = random_function()
        self.assertTrue(value, result)
        self.assertEqual(2, call_counts[0])
