Changelog
=========

v1.1
------

* Support for Django 1.9
* PEP8 cleanup
* Support for Python 3.5
* Drop support for Django < 1.7

v1.0.1
------

* Support for Django 1.8

v1.0
----

* Limited handling of filtered querysets (`qs.filter(pk=42).get()`) on Django 1.7+.
* Support ForeignKey lookups (when `use_for_related_fields = True` is set on the manager) on Django 1.7+.

v0.4
----

* Python 3 support
* `from_ids` now returns the model instances in the same order they were given in

v0.3
----

* `from_ids` can no longer be called on a manager not handled by django-ormcache
* Support for Django 1.6

v0.2
----

* Added signals for cache hits, misses and invalidations.
* Support wheel format for PyPI.

v0.1
----

* Initial Release
