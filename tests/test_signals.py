from django.core.cache import cache
from django.test import TestCase

from ormcache.signals import cache_hit, cache_missed, cache_invalidated
from tests.testapp.models import CachedDummyModel


class SignalsTestCase(TestCase):
    def setUp(self):
        self.call_count = 0
        self.instance_pk = CachedDummyModel.objects.create().pk
        cache.clear()

    def _signal_receiver(self):
        def inner(*args, **kwargs):
            self.call_count += 1

        return inner

    def test_cache_hit_signal(self):
        cache_hit.connect(self._signal_receiver(), weak=False)

        # Cache miss
        CachedDummyModel.objects.get(pk=self.instance_pk)
        self.assertEqual(0, self.call_count)

        # Cache hit
        CachedDummyModel.objects.get(pk=self.instance_pk)
        self.assertEqual(1, self.call_count)

    def test_cache_missed_signal(self):
        cache_missed.connect(self._signal_receiver(), weak=False)

        # Cache miss
        CachedDummyModel.objects.get(pk=self.instance_pk)
        self.assertEqual(1, self.call_count)

    def test_cache_invalidated_signal(self):
        cache_invalidated.connect(self._signal_receiver(), weak=False)

        # Cache miss
        instance = CachedDummyModel.objects.get(pk=self.instance_pk)
        self.assertEqual(0, self.call_count)

        # Save the object
        instance.title = "hello"
        instance.save()  # invalidate
        self.assertEqual(1, self.call_count)

    def test_cache_invalidate_on_delete_signal(self):
        cache_invalidated.connect(self._signal_receiver(), weak=False)

        # Cache miss
        instance = CachedDummyModel.objects.get(pk=self.instance_pk)
        self.assertEqual(0, self.call_count)

        # Delete the object
        instance.delete()
        self.assertEqual(1, self.call_count)
