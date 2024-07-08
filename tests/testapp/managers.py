import django
from django.db import models

from ormcache.managers import CachedManagerMixin


class DummyManager(CachedManagerMixin, models.Manager):
    if django.VERSION < (1, 10):
        use_for_related_fields = True
