import json
import os

DEBUG = True
SECRET_KEY = os.environ.get("ORMCACHE_TEST_DJANGO_SECRET_KEY", "ormcache")
SITE_ID = 1
TIME_ZONE = "UTC"
USE_TZ = True
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_DIR)

ALLOWED_HOSTS = json.loads(os.environ.get("ORMCACHE_TEST_ALLOWED_HOSTS_JSON", '["*"]'))

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        # use a on-disk db for test so --reuse-db can be used
        "TEST": {"NAME": os.path.join(BASE_DIR, "test_db.sqlite3")},
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "localhost",
        "OPTIONS": {
            "MAX_ENTRIES": 2**32,
        },
    }
}

ROOT_URLCONF = "tests.urls"
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "ormcache",
    "tests.testapp",
]

MIDDLEWARE = ("django.middleware.common.CommonMiddleware",)
