# OSD2F: Open Source Data Donation Framework

## Goal

Use OSD2F to run your own Data Donation service. The aim of this project is to facilitate 
scientists to collect data donations, by providing an easy-to-use web-based data donation 
platform. Here, scientists can instruct participants in their research to upload data 
exports from major online platforms (generally based on participants rights to their own
data under GDPR).

Currently supported donations: 
* None

## Using OSD2F locally

Installing the OSD2F locally is relatively simple by using pip's support for installation straight from 
VCS. However, we recommend local installation only in cases in which you want to familiarize yourself
with OSD2F and **never for production (real data collection) purposes**. 

### Installation

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

## See also:

1. [how to develop](docs/development.md)
