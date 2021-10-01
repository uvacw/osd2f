#!/usr/bin/env python

from setuptools import find_packages, setup

setup(
    name="OSD2F",
    python_requires="<3.9>3.8",
    version="0.1.0",
    description="Open Source Data Donation Framework",
    author="Bob van de Velde",
    author_email="osd2f@bob-as-a-service.com",
    license="TODO",
    url="https://github.com/uvacw/osd2f",
    packages=find_packages(),
    package_data={
        "osd2f": [
            "static/*",
            "templates/*",
            "templates/*/*",
            "settings/*",
            "static/js/*",
            "static/js/libarchive/*",
            "static/js/libarchive/wasm-gen/*",
        ]
    },
    scripts=["bin/osd2f"],
    install_requires=[
        "asyncpg",
        "azure-keyvault-secrets",
        "azure-identity",
        "cryptography",
        "hypercorn",
        "msal",
        "pyyaml",
        "pydantic",
        "pydantic[email]",
        "pyzipper",
        "quart",
        "tortoise-orm",
    ],
)
