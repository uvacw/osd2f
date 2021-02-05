#!/usr/bin/env python

from setuptools import setup

setup(
    name="OSD2F",
    python_requires=">-3.9",
    version="0.0-pre-release-alpha",
    description="Open Source Data Donation Framework",
    author="Bob van de Velde",
    author_email="osd2f@bob-as-a-service.com",
    license="TODO",
    url="https://github.com/uvacw/osd2f",
    packages=["osd2f"],
    scripts=["bin/osd2f"],
    install_requires=["quart", "pyyaml", "pydantic", "tortoise-orm", "asyncpg"],
)
