from django.core.cache import cache
from django.test import TestCase

from ormcache.tests.testapp.models import CachedDummyModel


class CachedQuerySetTestCase(TestCase):

    def setUp(self):
        self.instance1 = CachedDummyModel.objects.create()
        self.instance2 = CachedDummyModel.objects.create()
        self.pks = [self.instance1.pk, self.instance2.pk]
        cache.clear()

    def test_filter_in_cache(self):
        with self.assertNumQueries(1):
            instances = CachedDummyModel.objects.filter(pk__in=self.pks)
        self.assertEqual(2, len(instances))
        with self.assertNumQueries(0):
            instances = CachedDummyModel.objects.filter(pk__in=self.pks)
        self.assertEqual(2, len(instances))

        cache.clear()

        with self.assertNumQueries(1):
            instances = CachedDummyModel.objects.filter(id__in=self.pks)
        self.assertEqual(2, len(instances))
        with self.assertNumQueries(0):
            instances = CachedDummyModel.objects.filter(id__in=self.pks)
        self.assertEqual(2, len(instances))

    def test_filter_range_cache(self):
        with self.assertNumQueries(1):
            instances = CachedDummyModel.objects.filter(pk__range=self.pks)
        self.assertEqual(2, len(instances))
        with self.assertNumQueries(0):
            instances = CachedDummyModel.objects.filter(pk__range=self.pks)
        self.assertEqual(2, len(instances))

        cache.clear()

        with self.assertNumQueries(1):
            instances = CachedDummyModel.objects.filter(id__in=self.pks)
        self.assertEqual(2, len(instances))
        with self.assertNumQueries(0):
            instances = CachedDummyModel.objects.filter(id__in=self.pks)
        self.assertEqual(2, len(instances))

    def test_filter_invalid_pk(self):
        self.pks.append(self.instance1.pk + self.instance2.pk)

        with self.assertNumQueries(1):
            instances = list(CachedDummyModel.objects.filter(pk__in=self.pks))
        self.assertEqual(2, len(instances))

        with self.assertNumQueries(1):
            instances = list(CachedDummyModel.objects.filter(pk__in=self.pks))

    def test_filter_invalidation(self):
        with self.assertNumQueries(1):
            instances = CachedDummyModel.objects.filter(pk__in=self.pks)
        self.assertEqual(2, len(instances))

        CachedDummyModel.objects.invalidate(self.instance1.pk)

        with self.assertNumQueries(1):
            instances = CachedDummyModel.objects.filter(pk__in=self.pks)
        self.assertEqual(2, len(instances))

    def test_one_deferred_field(self):
        # This should not cache lesson since it contains a deferred field
        CachedDummyModel.objects.defer("title").get(pk=self.instance1.pk)

        with self.assertNumQueries(1):
            summary = CachedDummyModel.objects.get(
                pk=self.instance1.pk).summary

        self.assertEqual(self.instance1.summary, summary)

    def test_all_deferred_fields(self):
        # This should not cache lesson since it contains deferred fields
        CachedDummyModel.objects.only().get(pk=self.instance1.pk)

        with self.assertNumQueries(1):
            title = CachedDummyModel.objects.get(pk=self.instance1.pk).title

        self.assertEqual(self.instance1.title, title)
