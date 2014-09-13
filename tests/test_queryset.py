from django.core.cache import cache
from django.test import TestCase

from tests.testapp.models import CachedDummyModel


class CachedQuerySetTestCase(TestCase):

    def setUp(self):
        self.instance1 = CachedDummyModel.objects.create()
        self.instance2 = CachedDummyModel.objects.create()
        self.pks = [self.instance1.pk, self.instance2.pk]
        cache.clear()

    def test_from_ids_cache(self):
        with self.assertNumQueries(1):
            instances = CachedDummyModel.objects.from_ids(self.pks)
        self.assertEqual(2, len(instances))
        self.assertIsInstance(instances, list)

        with self.assertNumQueries(0):
            instances = CachedDummyModel.objects.from_ids(self.pks)
        self.assertEqual(2, len(instances))
        self.assertIsInstance(instances, list)

    def test_from_ids_invalid_pk(self):
        self.pks.append(self.instance1.pk + self.instance2.pk)

        with self.assertNumQueries(1):
            instances = CachedDummyModel.objects.from_ids(self.pks)
        self.assertEqual(2, len(instances))
        self.assertIsInstance(instances, list)

        with self.assertNumQueries(1):
            instances = CachedDummyModel.objects.from_ids(self.pks)
        self.assertIsInstance(instances, list)

    def test_from_ids_invalidation(self):
        with self.assertNumQueries(1):
            instances = CachedDummyModel.objects.from_ids(self.pks)
        self.assertEqual(2, len(instances))
        self.assertIsInstance(instances, list)

        CachedDummyModel.objects.invalidate(self.instance1.pk)

        with self.assertNumQueries(1):
            instances = CachedDummyModel.objects.from_ids(self.pks)
        self.assertEqual(2, len(instances))
        self.assertIsInstance(instances, list)

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
