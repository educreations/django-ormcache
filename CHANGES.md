Changelog
=========

v1.4
----

* Test on Django 4.2 through 5.2
* Test on Python 3.8 through 3.12
* Drop support for Django < 4.2 and Python < 3.8


v1.3.2
----

Another publish fix

v1.3.1
----

Unpublish.

v1.3
----

* Test on Django 2.0 through 4.2.
* Test on Python 3.7 through 3.12
* Stop testing on Python 2.7 and 3.6
* Stop testing and drop support for Django 1.9 and 1.10

v1.2.2
----

* TBD

v1.2.1
----

* TBD

v1.2
----

* Truncate cache keys to 250 characters, as Memcache requires smaller keys

v1.1.1
------

* Test on Django 1.10 [#40](https://github.com/educreations/django-ormcache/pull/40)
* Invalidation after delete does not log an error [#41](https://github.com/educreations/django-ormcache/pull/41)

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
