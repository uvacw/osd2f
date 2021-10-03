![Python application](https://github.com/uvacw/osd2f/workflows/Python%20application/badge.svg?branch=main)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
# OSD2F: Open Source Data Donation Framework

## Goal

Use OSD2F to run your own Data Donation service. The aim of this project is to facilitate 
scientists to collect data donations, by providing an easy-to-use web-based data donation 
platform. Here, scientists can instruct participants in their research to upload data 
exports from major online platforms (generally based on participants rights to their own
data under GDPR).

The App aims to be as export agnostic as possible while keeping things feasible to maintain.
You can specify the files and the whitelist of JSON fields through YAML configuration. 
As such it supports Data Donation Packages of arbitrary format in JSON files. 

## Using OSD2F locally

Installing the OSD2F locally is relatively simple by using pip's support for installation straight from 
VCS. However, we recommend local installation only in cases in which you want to familiarize yourself
with OSD2F and **never for production (real data collection) purposes**. 

***Note:** There is a different set of instructions for development purposes in the [development docs](docs/development.md)*

### Installation (not for development)

OSD2F requires python 3.8 or up, check your version by running:

```bash
python --version
```
should say something like:
> Python 3.8.0

*Note: it's recommended to use a virtual environment, please consult de [development docs](docs/development.md) for more information.*

```bash
pip install git+https://github.com/uvacw/osd2f
```

### Running

```bash
osd2f -h # see help
```

```bash
osd2f -m Testing # to run a testing instance
```

You can configure the text content of the webpages. The easiest way to get started
is by generating a YAML file with the default values and editing it to your liking:

```bash
osd2f --generate-current-config config.yaml
```

You can start the server with this content configuration by passing a file-path 
via the CLI. 

```bash
osd2f --content-configuration config.yaml # make sure you've edited it first
```

***Note**: OSD2F will store the configuration in the database. In development mode, the
most recently edited version is used between the database and the file.*

## See also:

1. [how to develop](docs/development.md)
2. [Deploying to Azure](docs/deploying_to_azure.md)
3. [Running stresstests](docs/stresstests.md)
4. [Testing the researcher login with basic auth](docs/basic_authentication.md)
5. [Using Microsoft Authentication via SSO](docs/microsoft_authentication.md)
6. [Setting password on researcher downloads](docs/protecting_downloads.md)
