#!/usr/bin/env python

from setuptools import find_packages, setup

setup(
    name="OSD2F",
    python_requires=">=3.9",
    version="0.0-pre-release-alpha",
    description="Open Source Data Donation Framework",
    author="Bob van de Velde",
    author_email="osd2f@bob-as-a-service.com",
    license="TODO",
    url="https://github.com/uvacw/osd2f",
    packages=find_packages(),
    package_data={"osd2f": ["static/*", "templates/*", "settings/*"]},
    scripts=["bin/osd2f"],
    install_requires=["quart", "pyyaml", "pydantic"],
)
