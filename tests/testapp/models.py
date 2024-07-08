import django
from django.db import models

from tests.testapp.managers import DummyManager


class CachedDummyModel(models.Model):
    cache_enabled = True

    title = models.CharField(max_length=50)
    summary = models.CharField(max_length=400)

    related = models.ForeignKey(
        "OtherCachedDummyModel", null=True, on_delete=models.SET_NULL
    )

    objects = DummyManager()

    class Meta(object):
        if django.VERSION >= (1, 10):
            base_manager_name = "objects"
            default_manager_name = "objects"


class OtherCachedDummyModel(models.Model):
    cache_enabled = True

    objects = DummyManager()

    class Meta(object):
        if django.VERSION >= (1, 10):
            base_manager_name = "objects"
            default_manager_name = "objects"


class UncachedDummyModel(models.Model):
    title = models.CharField(max_length=50)
    summary = models.CharField(max_length=400)

    objects = DummyManager()

    class Meta(object):
        if django.VERSION >= (1, 10):
            base_manager_name = "objects"
            default_manager_name = "objects"
