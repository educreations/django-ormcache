from django.test import SimpleTestCase

from tests.testapp.models import CachedDummyModel, UncachedDummyModel


class BaseManagerCacheTestCase(SimpleTestCase):
    def test_cache_key_on_uncached(self):
        with self.assertRaises(RuntimeError):
            UncachedDummyModel.objects.cache_key(1)

    def test_invalidate_on_uncached(self):
        with self.assertRaises(RuntimeError):
            UncachedDummyModel.objects.invalidate(1)

    def test_cache_key_on_cached(self):
        try:
            cache_key = CachedDummyModel.objects.cache_key(1)
        except RuntimeError:
            self.fail("Should not have raised exception")
        self.assertIsNotNone(cache_key)

    def test_invalidate_on_cached(self):
        try:
            CachedDummyModel.objects.invalidate(1)
        except RuntimeError:
            self.fail("Should not have raised exception")
