from django.db.models.signals import class_prepared, post_delete, post_save
from django.utils.functional import cached_property

from ormcache.queryset import CachedQuerySet


class CachedManagerMixin(object):

    @cached_property
    def __cache_enabled(self):
        return getattr(self.model, "cache_enabled", False)

    def __require_cache(func):
        def wrapper(self, *args, **kwargs):
            if not self.__cache_enabled:
                error = "Caching is not enabled on {}".format(str(type(self)))
                raise RuntimeError(error)
            return func(self, *args, **kwargs)
        return wrapper

    def from_ids(self, ids, lookup='pk__in', **kwargs):
        queryset = self.get_query_set()
        if not self.__cache_enabled:
            return queryset.filter(**{lookup: ids})
        return queryset.from_ids(ids, lookup=lookup, **kwargs)

    @__require_cache
    def invalidate(self, *args, **kwargs):
        return self.get_query_set().invalidate(*args, **kwargs)

    @__require_cache
    def cache_key(self, *args, **kwargs):
        return self.get_query_set().cache_key(*args, **kwargs)

    # Django overrides

    def contribute_to_class(self, model, name):
        """
        Overrides Django builtin
        """
        super(CachedManagerMixin, self).contribute_to_class(model, name)
        class_prepared.connect(self.__class_prepared_cache, sender=model)

    def get_query_set(self):
        """
        Overrides Django builtin
        """
        if self.__cache_enabled:
            return CachedQuerySet(self.model)
        else:
            return super(CachedManagerMixin, self).get_query_set()

    # Signals

    def __class_prepared_cache(self, sender, **kwargs):
        if self.__cache_enabled:
            post_save.connect(self.__post_save_cache,
                              sender=self.model, weak=False)
            post_delete.connect(self.__post_delete_cache,
                                sender=self.model, weak=False)

    def __post_save_cache(self, instance, created, **kwargs):
        self.invalidate(instance.pk, recache=True)

    def __post_delete_cache(self, instance, **kwargs):
        self.invalidate(instance.pk)
