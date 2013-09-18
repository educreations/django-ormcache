from django.db import models

from ormcache.tests.testapp.managers import DummyManager


class CachedDummyModel(models.Model):

    cache_enabled = True

    title = models.CharField(max_length=50)
    summary = models.CharField(max_length=400)

    objects = DummyManager()


class UncachedDummyModel(models.Model):

    title = models.CharField(max_length=50)
    summary = models.CharField(max_length=400)

    objects = DummyManager()
