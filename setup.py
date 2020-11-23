#!/usr/bin/env python

from distutils.core import setup

setup(
    name="OSD2F",
    version="0.0-pre-release-alpha",
    description="Open Source Data Donation Framework",
    author="Bob van de Velde",
    author_email="osd2f@bob-as-a-service.com",
    license="TODO",
    url="",
    packages=["osd2f"],
    scripts=["bin/osd2f"],
    install_requires=["quart"],
)
