#!/usr/bin/env python

from setuptools import find_packages, setup

setup(
    name="OSD2F",
    python_requires="<3.9>3.8",
    version="0.0.4",
    description="Open Source Data Donation Framework",
    author="Bob van de Velde",
    author_email="osd2f@bob-as-a-service.com",
    license="TODO",
    url="https://github.com/uvacw/osd2f",
    packages=find_packages(),
    package_data={"osd2f": ["static/*", "templates/*", "settings/*", "static/js/*"]},
    scripts=["bin/osd2f"],
    # quart is version pinned due to a bug in the 0.14.X versions
    # pending resolution of: https://gitlab.com/pgjones/quart/-/issues/398
    install_requires=[
        "quart",
        "pyyaml",
        "pydantic",
        "tortoise-orm",
        "asyncpg",
        "hypercorn",
        "msal",
    ],
)
