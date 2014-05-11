import logging

from django.core.cache import cache
from django.db.models.query import QuerySet

from ormcache.signals import cache_hit, cache_missed, cache_invalidated

log = logging.getLogger(__name__)


class CachedQuerySet(QuerySet):

    __CACHE_FOREVER = 2592000  # http://ur1.ca/egyvu

    @staticmethod
    def __is_filtered(query):
        return len(query.where.children) > 0

    @staticmethod
    def __is_deferred(query):
        return (len(query.deferred_loading[0]) > 0 or
                not query.deferred_loading[1])

    def get(self, *args, **kwargs):
        """
        Adds a layer of caching around the Manager's built in 'get()' method.
        Will only cache if 'pk' or 'id' is used in kwargs. Results from the
        'get()' method will be cached indefinitely (30 days) until invalidated.
        """

        # Don't access cache if using a filtered or deferred queryset
        if self.__is_filtered(self.query) or self.__is_deferred(self.query):
            return super(CachedQuerySet, self).get(*args, **kwargs)

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
            return super(CachedQuerySet, self).get(*args, **kwargs)

        key = self.cache_key(pk)

        # Retrieve (or set) the item in the cache
        item = cache.get(key)
        if item is None:
            cache_missed.send(sender=self.model)
            item = super(CachedQuerySet, self).get(*args, **kwargs)
            cache.set(key, item, self.__CACHE_FOREVER)
        else:
            cache_hit.send(sender=self.model)

        return item

    def filter(self, *args, **kwargs):

        # Don't access cache if using a filtered or deferred queryset
        if self.__is_filtered(self.query) or self.__is_deferred(self.query):
            return super(CachedQuerySet, self).filter(*args, **kwargs)

        if len(kwargs) > 1:
            return super(CachedQuerySet, self).filter(*args, **kwargs)

        lookup, value = kwargs.items()[0]

        if lookup in ['pk__in', 'id__in']:
            ids = value
        elif lookup in ['pk__range', 'id__range']:
            ids = range(value[0], value[1] + 1)
        else:
            return super(CachedQuerySet, self).filter(*args, **kwargs)

        cache_keys = [self.cache_key(id_) for id_ in ids]

        cached = cache.get_many(cache_keys)
        cached_instances = [i for i in cached.values() if i]
        cached_ids = {instance.pk for instance in cached_instances}
        uncached_ids = set(ids) - cached_ids

        # If there are uncached instances, retrieve and cache them
        if len(uncached_ids) > 0:
            uncached = super(CachedQuerySet, self).filter(pk__in=uncached_ids)

            # Add the uncached instances to the existing instances
            cached_instances += uncached

            # Cache the uncached instances
            to_cache = {self.cache_key(i.pk): i for i in uncached}
            cache.set_many(to_cache, self.__CACHE_FOREVER)

        return cached_instances

    def cache_key(self, pk):
        """
        Generate the cache key for an individual model
        """
        return "{}-pk:{}".format(self.model.__name__, pk)

    def invalidate(self, pk, recache=False):
        """
        Invalidate a single item in the cache
        """
        key = self.cache_key(pk)
        cache_invalidated.send(sender=self.model)
        if recache is True:
            try:
                entry = super(CachedQuerySet, self).get(pk=pk)
            except (self.model.DoesNotExist,
                    self.model.MultipleObjectsReturned):
                log.error(
                    'Error retrieving single entry from database',
                    exc_info=True,
                    extra={'data': {'model': self.model, 'pk': pk}})
            else:
                cache.set(key, entry, self.__CACHE_FOREVER)
        else:
            cache.delete(key)
