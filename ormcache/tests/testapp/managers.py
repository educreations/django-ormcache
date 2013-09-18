from django.db import models

from ormcache.managers import CachedManagerMixin


class DummyManager(CachedManagerMixin, models.Manager):

    use_for_related_fields = True
