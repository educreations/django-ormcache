#!/usr/bin/env python

# Setup Django

from django.conf import settings

settings.configure(
    DEBUG=True,
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
        },
    },
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'localhost',
            'OPTIONS': {
                'MAX_ENTRIES': 2 ** 32,
            },
        },
    },
    INSTALLED_APPS=(
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'ormcache',
        'ormcache.tests.testapp',
    ),
    TEST_RUNNER='django_nose.NoseTestSuiteRunner',
)


# Run tests

import sys

from django_nose import NoseTestSuiteRunner


test_runner = NoseTestSuiteRunner(verbosity=1)
test_runner.setup_databases()
failures = test_runner.run_tests(['ormcache', ])
if failures:
    sys.exit(failures)
