import collections
import logging

import django
from django.core.cache import cache
from django.db.models.query import QuerySet

if django.VERSION >= (1, 8):
    from django.db.models.expressions import Col
    from django.db.models.lookups import Exact
elif django.VERSION >= (1, 7):
    from django.db.models.lookups import Exact
    from django.db.models.sql.datastructures import Col

from ormcache.signals import cache_hit, cache_missed, cache_invalidated  # noqa

log = logging.getLogger(__name__)


class CachedQuerySet(QuerySet):

    __CACHE_FOREVER = 2592000  # http://ur1.ca/egyvu

    def get(self, *args, **kwargs):
        """
        Adds a layer of caching around the Manager's built in 'get()' method.
        Will only cache if 'pk' or 'id' is used in kwargs. Results from the
        'get()' method will be cached indefinitely (30 days) until invalidated.
        """

        orig_kwargs = kwargs.copy()

        # If this queryset is filtered by a single column and no arguments
        # were passed to get(), treat the queryset filter as an argument to
        # get(). This lets Model.objects.filter(pk=42).get() work like
        # Model.objects.get(pk=42).
        can_ignore_filter = False
        if (len(self.query.where) == 1 and
                not kwargs and
                django.VERSION >= (1, 7) and
                not self.query.where.negated):
            child, = self.query.where.children
            if isinstance(child, Exact) and isinstance(child.lhs, Col):
                can_ignore_filter = True
                kwargs[child.lhs.target.attname] = child.rhs

        # Don't access cache if using a filtered queryset
        if self.query.where and not can_ignore_filter:
            return super(CachedQuerySet, self).get(*args, **orig_kwargs)

        # Don't access cache if using a deferred queryset
        if len(self.query.deferred_loading[0]) > 0 or \
                not self.query.deferred_loading[1]:
            return super(CachedQuerySet, self).get(*args, **orig_kwargs)

        # Get the cache key from the model name and pk
        if "pk" in kwargs:
            pk = kwargs["pk"]
        elif "pk__exact" in kwargs:
            pk = kwargs["pk__exact"]
        elif "id" in kwargs:
            pk = kwargs["id"]
        elif "id__exact" in kwargs:
            pk = kwargs["id__exact"]
        else:
            return super(CachedQuerySet, self).get(*args, **orig_kwargs)

        key = self.cache_key(pk)

        # Retrieve (or set) the item in the cache
        item = cache.get(key)
        if item is None:
            cache_missed.send(sender=self.model)
            item = super(CachedQuerySet, self).get(*args, **orig_kwargs)
            cache.set(key, item, self.__CACHE_FOREVER)
        else:
            cache_hit.send(sender=self.model)

        return item

    def from_ids(self, ids, lookup='pk__in'):
        assert isinstance(ids, collections.Iterable)

        cache_keys = [self.cache_key(id_) for id_ in ids]

        instances = cache.get_many(cache_keys).values()
        cached_dict = {i.id: i for i in instances if i}
        uncached_ids = set(ids) - set(cached_dict.keys())

        # If there are uncached instances, retrieve and cache them
        if len(uncached_ids) > 0:
            uncached = self.filter(**{lookup: uncached_ids})

            # Add the uncached instances to the existing instances
            cached_dict.update((i.id, i) for i in uncached)

            # Cache the uncached instances
            to_cache = {self.cache_key(i.pk): i for i in uncached}
            cache.set_many(to_cache, self.__CACHE_FOREVER)

        return [cached_dict[id_] for id_ in ids if id_ in cached_dict]

    def cache_key(self, pk):
        """Generate the cache key for an individual model"""
        return "{}-pk:{}".format(self.model.__name__, pk)

    def invalidate(self, pk, recache=False):
        """Invalidate a single item in the cache"""
        key = self.cache_key(pk)
        cache_invalidated.send(sender=self.model)
        if recache is True:
            try:
                entry = super(CachedQuerySet, self).get(pk=pk)
            except self.model.DoesNotExist:
                log.info(
                    'Unable to recache model during invalidate',
                    exc_info=True,
                    extra={'data': {'model': self.model, 'pk': pk}})
            except self.model.MultipleObjectsReturned:
                log.error(
                    'Error retrieving single entry from database',
                    exc_info=True,
                    extra={'data': {'model': self.model, 'pk': pk}})
            else:
                cache.set(key, entry, self.__CACHE_FOREVER)
        else:
            cache.delete(key)
