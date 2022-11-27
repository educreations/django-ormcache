import django
from django.core.cache import cache
from django.test import TestCase

from tests.testapp.models import (
    CachedDummyModel,
    OtherCachedDummyModel,
    UncachedDummyModel,
)


class UncachedModelQuerySetTestCase(TestCase):
    def setUp(self):
        self.instance = UncachedDummyModel.objects.create()
        cache.clear()

    def test_no_cache(self):
        with self.assertNumQueries(1):
            UncachedDummyModel.objects.get(pk=self.instance.pk)

        # Should still be one query
        with self.assertNumQueries(1):
            UncachedDummyModel.objects.get(pk=self.instance.pk)


class CachedQuerySetTestCase(TestCase):
    def setUp(self):
        self.instance1 = CachedDummyModel.objects.create()
        self.instance2 = CachedDummyModel.objects.create()
        self.pks = [self.instance1.pk, self.instance2.pk]
        cache.clear()

    def test_filter_get_nocache(self):
        # Get the cache key for an instance, make sure it doesn't exist
        cache_key = CachedDummyModel.objects.cache_key(self.instance1.pk)
        self.assertIsNone(cache.get(cache_key))

        # Use .get() after .filter() with no args, should set cache
        with self.assertNumQueries(1):
            CachedDummyModel.objects.filter().get(pk=self.instance1.pk)
            CachedDummyModel.objects.filter().get(pk=self.instance1.pk)
        self.assertIsNotNone(cache.get(cache_key))
        cache.clear()

        # Use .get() after .filter(...), should not set cache
        with self.assertNumQueries(2):
            CachedDummyModel.objects.filter(pk__gt=0).get(pk=self.instance1.pk)
            CachedDummyModel.objects.filter(pk__gt=0).get(pk=self.instance1.pk)
        self.assertIsNone(cache.get(cache_key))

        # Use .get() after .filter(pk=), should set cache
        if django.VERSION >= (1, 7):
            with self.assertNumQueries(1):
                CachedDummyModel.objects.filter(pk=self.instance1.pk).get()
                CachedDummyModel.objects.filter(pk=self.instance1.pk).get()
            self.assertIsNotNone(cache.get(cache_key))
            cache.clear()

        # Use .get() with another getter and modifier
        with self.assertNumQueries(2):
            kwargs = {"pk__gte": self.instance1.pk, "pk__lte": self.instance1.pk}
            CachedDummyModel.objects.get(**kwargs)
            CachedDummyModel.objects.get(**kwargs)
        self.assertIsNone(cache.get(cache_key))

        # Use .get() with various pk getters, and cache should be set
        for pk_id in ("pk", "id"):
            for modifier in ("", "__exact"):
                with self.assertNumQueries(1):
                    kwargs = {"{}{}".format(pk_id, modifier): self.instance1.pk}
                    CachedDummyModel.objects.get(**kwargs)
                    CachedDummyModel.objects.get(**kwargs)
                self.assertIsNotNone(cache.get(cache_key))
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
            summary = CachedDummyModel.objects.get(pk=self.instance1.pk).summary

        self.assertEqual(self.instance1.summary, summary)

    def test_all_deferred_fields(self):
        # This should not cache lesson since it contains deferred fields
        CachedDummyModel.objects.only().get(pk=self.instance1.pk)

        with self.assertNumQueries(1):
            title = CachedDummyModel.objects.get(pk=self.instance1.pk).title

        self.assertEqual(self.instance1.title, title)
        cache.clear()

    def test_invalidated_after_delete(self):
        # Get the cache key for an instance, make sure it doesn't exist
        cache_key = CachedDummyModel.objects.cache_key(self.instance1.pk)
        self.assertIsNone(cache.get(cache_key))

        instance_pk = self.instance1.pk

        with self.assertNumQueries(1):
            CachedDummyModel.objects.get(pk=self.instance1.pk)

        # Delete the instance
        with self.assertNumQueries(1):
            self.instance1.delete()

        # Nothing should be in the cache
        self.assertIsNone(cache.get(cache_key))

        # Fetching should raise
        with self.assertRaises(CachedDummyModel.DoesNotExist):
            CachedDummyModel.objects.get(pk=instance_pk)

        # Make sure that invalidation does not raise an exception
        CachedDummyModel.objects.invalidate(pk=instance_pk, recache=True)
        self.assertIsNone(cache.get(cache_key))


class CachedQuerySetRelatedTestCase(TestCase):
    def setUp(self):
        self.other_dummy = OtherCachedDummyModel.objects.create()
        self.dummy = CachedDummyModel.objects.create()
        self.dummy.related = self.other_dummy
        self.dummy.save()
        cache.clear()

    def test_no_related_cache(self):
        with self.assertNumQueries(2):
            instance = OtherCachedDummyModel.objects.get(pk=self.other_dummy.pk)
            related_pks = [
                related.pk for related in instance.cacheddummymodel_set.all()
            ]
            self.assertIn(self.dummy.pk, related_pks)

        with self.assertNumQueries(1):
            list(
                OtherCachedDummyModel.objects.get(
                    pk=self.other_dummy.pk
                ).cacheddummymodel_set.all()
            )

    def test_related_cache(self):
        with self.assertNumQueries(2):
            self.assertEqual(
                self.other_dummy.pk,
                CachedDummyModel.objects.get(pk=self.dummy.pk).related.pk,
            )

        with self.assertNumQueries(0):
            self.assertEqual(
                self.other_dummy.pk,
                CachedDummyModel.objects.get(pk=self.dummy.pk).related.pk,
            )
