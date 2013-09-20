from django.core.cache import cache
from django.test import SimpleTestCase

from ormcache.signals import cache_hit, cache_missed, cache_invalidated
from ormcache.tests.testapp.models import CachedDummyModel


class SignalsTestCase(SimpleTestCase):

    def setUp(self):
        self.signal_called = False
        self.instance_pk = CachedDummyModel.objects.create().pk
        cache.clear()

    def tearDown(self):
        self._disconnect_signals()

    def _disconnect_signals(self):
        cache_hit.disconnect(self._signal_callback)
        cache_missed.disconnect(self._signal_callback)
        cache_invalidated.disconnect(self._signal_callback)

    def _signal_callback(self, sender, signal):
        self.signal_called = True
        self.assertEquals(sender, CachedDummyModel)

    def test_cache_hit_signal(self):
        cache_hit.connect(self._signal_callback)

        CachedDummyModel.objects.get(pk=self.instance_pk)  # miss
        self.assertFalse(self.signal_called)
        CachedDummyModel.objects.get(pk=self.instance_pk)  # hit
        self.assertTrue(self.signal_called)

    def test_cache_missed_signal(self):
        cache_missed.connect(self._signal_callback)

        CachedDummyModel.objects.get(pk=self.instance_pk)  # miss
        self.assertTrue(self.signal_called)

    def test_cache_invalidated_signal(self):
        cache_invalidated.connect(self._signal_callback)

        instance = CachedDummyModel.objects.get(pk=self.instance_pk)  # miss
        self.assertFalse(self.signal_called)
        instance.title = "hello"
        instance.save()  # invalidate
        self.assertTrue(self.signal_called)
