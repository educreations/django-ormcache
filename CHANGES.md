Changelog
=========

v0.3
----

`from_ids` has been removed. Use `filter(pk__in=...)` to accomplish the same thing.
kwargs for filter (pk__in, id__in, pk__range, id__range) all now attempt to pull from the cache.

v0.2
----

Added signals for cache hits, misses and invalidations.
Support wheel format for PyPI.

v0.1
----

Initial Release
