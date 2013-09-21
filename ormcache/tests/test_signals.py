from django.core.cache import cache
from django.test import TestCase
from mock_django.signals import mock_signal_receiver

from ormcache.signals import cache_hit, cache_missed, cache_invalidated
from ormcache.tests.testapp.models import CachedDummyModel


class SignalsTestCase(TestCase):

    def setUp(self):
        self.instance_pk = CachedDummyModel.objects.create().pk
        cache.clear()

    def test_cache_hit_signal(self):
        with mock_signal_receiver(cache_hit, sender=CachedDummyModel) as receiver:
            # Cache miss
            CachedDummyModel.objects.get(pk=self.instance_pk)
            self.assertEquals(0, receiver.call_count)

            # Cache hit
            CachedDummyModel.objects.get(pk=self.instance_pk)
            self.assertEquals(1, receiver.call_count)

    def test_cache_missed_signal(self):
        with mock_signal_receiver(cache_missed, sender=CachedDummyModel) as receiver:
            # Cache miss
            CachedDummyModel.objects.get(pk=self.instance_pk)
            self.assertEquals(1, receiver.call_count)

    def test_cache_invalidated_signal(self):
        with mock_signal_receiver(cache_invalidated, sender=CachedDummyModel) as receiver:
            # Cache miss
            instance = CachedDummyModel.objects.get(pk=self.instance_pk)
            self.assertEquals(0, receiver.call_count)

            # Save the object
            instance.title = "hello"
            instance.save()  # invalidate
            self.assertEquals(1, receiver.call_count)
