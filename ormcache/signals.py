import django.dispatch


cache_hit = django.dispatch.Signal()
cache_missed = django.dispatch.Signal()
cache_invalidated = django.dispatch.Signal()
