from django.db.models.signals import class_prepared, post_delete, post_save
from django.utils.functional import cached_property

from ormcache.queryset import CachedQuerySet


class CachedManagerMixin(object):

    @cached_property
    def _cache_enabled(self):
        return getattr(self.model, "cache_enabled", False)

    def _require_cache(func):
        def wrapper(self, *args, **kwargs):
            if not self._cache_enabled:
                error = "Caching is not enabled on {}".format(str(type(self)))
                raise RuntimeError(error)
            return func(self, *args, **kwargs)
        return wrapper

    def from_ids(self, ids, lookup='pk__in', **kwargs):
        queryset = self.get_query_set()
        if not self._cache_enabled:
            return queryset.filter(**{lookup: ids})
        return queryset.from_ids(ids, lookup=lookup, **kwargs)

    @_require_cache
    def invalidate(self, *args, **kwargs):
        return self.get_query_set().invalidate(*args, **kwargs)

    @_require_cache
    def cache_key(self, *args, **kwargs):
        return self.get_query_set().cache_key(*args, **kwargs)

    # Django overrides

    def contribute_to_class(self, model, name):
        """
        Overrides Django builtin
        """
        super(CachedManagerMixin, self).contribute_to_class(model, name)
        class_prepared.connect(self._class_prepared_cache, sender=model)

    def get_query_set(self):
        """
        Overrides Django builtin
        """
        if self._cache_enabled:
            return CachedQuerySet(self.model)
        else:
            return super(CachedManagerMixin, self).get_query_set()

    # Signals

    def _class_prepared_cache(self, sender, **kwargs):
        if self._cache_enabled:
            post_save.connect(self._post_save_cache,
                              sender=self.model, weak=False)
            post_delete.connect(self._post_delete_cache,
                                sender=self.model, weak=False)

    def _post_save_cache(self, instance, created, **kwargs):
        self.invalidate(instance.pk, recache=True)

    def _post_delete_cache(self, instance, **kwargs):
        self.invalidate(instance.pk)
