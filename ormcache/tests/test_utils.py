from django.core.cache import cache
from django import test

from ormcache.tests.testapp.models import (
    CachedDummyModel,
    OtherCachedDummyModel,
)
from ormcache.utils import attach_foreignkey


class AttachForeignkeyTestCase(test.TestCase):

    def setUp(self):
        self.instance = CachedDummyModel.objects.create()
        self.related_instance = OtherCachedDummyModel.objects.create()

        self.instance.related = self.related_instance
        self.instance.save()

        cache.clear()

    def test_attach_foreignkey(self):
        instances = list(CachedDummyModel.objects.all())

        cache_key = OtherCachedDummyModel.objects.cache_key(
            self.related_instance.pk)

        self.assertFalse(cache_key in cache)

        with self.assertNumQueries(1):
            attach_foreignkey(instances, CachedDummyModel.related)

        self.assertTrue(cache_key in cache)

        with self.assertNumQueries(0):
            attach_foreignkey(instances, CachedDummyModel.related)
