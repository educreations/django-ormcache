try:
    from django.db.models.fields.related import SingleRelatedObjectDescriptor
except ImportError:
    from django.db.models.fields.related_descriptors import (
        ReverseOneToOneDescriptor as SingleRelatedObjectDescriptor,
    )


def _distinct(l):
    """Given an iterable will return a list of all distinct values."""
    return list(set(l))


def attach_foreignkey(objects, field):
    """
    Similar to the disqus's attach_foreignkey, but pulls items from the cache
    if caching is enabled on the model
    """
    is_foreignkey = isinstance(field, SingleRelatedObjectDescriptor)

    if not is_foreignkey:
        field = field.field
        accessor = "_%s_cache" % field.name
        model = field.remote_field.model
        lookup = "%s__in" % "pk"
        column = field.column
        key = "pk"
    else:
        accessor = field.cache_name
        field = field.related.field
        model = field.model
        lookup = "%s__in" % field.name
        column = "pk"
        key = field.column

    # Ensure values are unique, do not contain already present values, and
    # are not missing values specified in select_related
    values = _distinct(
        getattr(o, column) for o in objects if getattr(o, accessor, False) is False
    )
    if not values:
        return

    # Pull instances from cache if caching is enabled. This conditional logic
    # can be removed when the UserManager inherits BaseManager
    if getattr(model, "cache_enabled", False) is True:
        instances = model.objects.from_ids(values, lookup=lookup)
    else:
        instances = model.objects.filter(**{lookup: values})

    instances_dict = {getattr(i, key): i for i in instances}

    for obj in objects:
        setattr(obj, accessor, instances_dict.get(getattr(obj, column)))
