from setuptools import setup

readme_text = open("README.rst", "rb").read()

setup(
    name="django-ormcache",
    version="0.1",
    description="ORM cache for Django",
    license="BSD",
    keywords="cache django",
    author="Corey Farwell",
    author_email="coreyf@rwell.org",
    maintainer="Corey Farwell",
    maintainer_email="coreyf@rwel.org",
    url="https://github.com/educreations/django-ormcache",
    long_description=readme_text,
    packages=["ormcache"],
    package_dir={"ormcache": "ormcache"},
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ]
)
