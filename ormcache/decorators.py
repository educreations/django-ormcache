from hashlib import sha1
import logging

from django.core.cache import cache
from django.utils.decorators import wraps

log = logging.getLogger(__name__)


def cache_result(ttl=60 * 5, key=None):
    """
    Cache the result of a function call using Django's caching mechanism.

    If the decorated function returns None, cache_result raises a
    RuntimeException (as the cache returns None to indicate a miss).

    Note: If a key is not passed, the decorator will hash the function
    signature. The ordering of function parameters is important. e.g.:
    * myFunction(x=1, y=2)
    * myFunction(y=2, x=1)
    * myFunction(1, 2)
    will each be cached separately.

    Note: Does not automatically handle invalidation

    Usage:
    --------------------------------------------------------------------------
    @cache_result
    def my_expensive_method(param1, param2, param3):
        ....
        return expensive_result
    --------------------------------------------------------------------------
    """

    def decorator(func):
        @wraps(func)
        def inner(*args, **kwargs):
            key_ = key
            if key_ is None:
                func_signature = (
                    str(func.__module__) + str(func.__name__) + str(args) + str(kwargs)
                ).encode("utf8")
                key_ = sha1(func_signature).hexdigest()
            result = cache.get(key_)
            if result is None:
                result = func(*args, **kwargs)
                if result is None:
                    log.error(
                        "Function decorated by @cache_result returned " "None",
                        extra={"function": func.__name__},
                    )
                cache.set(key_, result, ttl)
            return result

        return inner

    return decorator
