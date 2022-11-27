from django.db import models

from ormcache.managers import CachedManagerMixin


class DummyManager(CachedManagerMixin, models.Manager):

    # Remove after Django 1.10 is the only supported backend
    use_for_related_fields = True
