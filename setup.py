from setuptools import setup, find_packages


readme_text = open("README.md", "r").read()

setup(
    name="django-ormcache",
    version="1.3",
    description="ORM cache for Django",
    license="MIT",
    keywords="cache django",
    author="Corey Farwell",
    author_email="coreyf@rwell.org",
    maintainer="Educreations Engineering",
    maintainer_email="engineering@educreations.com",
    url="https://github.com/educreations/django-ormcache",
    long_description=readme_text,
    long_description_content_type="text/markdown",
    packages=find_packages(where="ormcache"),
    package_dir={"ormcache": "ormcache"},
    python_requires=">=3.7, <4",
    install_requires=["Django>=2.0,<5.0", "six"],
    classifiers=[
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development",
    ],
    extras_require={"test": ["tox", "pytest", "pytest-django", "flake8"]},
    tests_require=["django-ormcache[test]"],
    project_urls={
        "Homepage": "https://github.com/educreations/django-ormcache",
        "Issues": "https://github.com/educreations/django-ormcache/issues",
        "Changelog": "https://github.com/educreations/django-ormcache/blob/master/CHANGES.md",
    },
)
