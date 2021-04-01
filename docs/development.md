# Development

## Core assumptions

Choices in this codebase are based on some assumptions as to the uses of the
framework. Because of these assumptions some things are simple, whereas others
are harder. When contributing code, please make sure you keep these assumptions
in mind:

- **Functionality should be generic over many kinds of donation formats**. 
This means that the frontend, endpoints, anonymizers and configurations should be able to handle pretty arbitrary JSON*. Assumptions about existing fields, datatypes etcetera should be limited to
  - the default configuration file example
  - export source specific anonymizers
- **Configuration targets users with low technical expertise**, 
which means the selection of fields to include and anonymizers to use should be relatively easy to infer from the example configuration. It also means that we want to avoid making content decisions in code.
- **This framework is for collection, *not* analysis**. 
The intended use of this framework is to provide a participant facing data submission interface with good privacy guarantees. The researchers who administer the deployment can download the data to do analysis in their own environment. The entries submitted can therefore be treated as a 'black box'. This helps maintain flexibility (no database migrations for new donation types) and maintainability (changes in export formats can be upgraded via configuration only).
- **All content data is sensitive** and should never be in any logs or 
  (disk) storage UNLESS after the explicit consent step. This also means
  that AT NO POINT any of the JSON fields or values should be in a 
  `print()`, `logger.info()`, `logger.warning()`, `logger.critical()` or any other stdout/stderr statement. For local development and testing purposes,
  you can use `logger.debug()` to contain content information.


## Installation for development

You can install this Python Package for local development purposes. To do 
so, we *strongly* advice using a virtual environment context. 

In addition, please note that OSD2F was written for Python `3.8.0`. Using
a virtual environment should make it easy to install this version without impacting your other Python projects.

----
##### Example using the popular [anaconda distribution of python](https://www.anaconda.com/)

```bash 
conda create -n osd2f python=3.8 # only required once
conda activate osd2f # run at the start of each osd2f development session
```
----

### 1. Clone the repository

You can clone the git repository so you can easily switch between branches.

```bash
# get the repository
git clone git@github.com:uvacw/osd2f.git
# move to project ROOT
cd osd2f
# you know you're in the right place if it contains setup.py
ls setup.py
# shows: `setup.py`, if it says 'cannot access' you in the wrong place
```

### 2. Install the package in editable mode

For development purposes, you should install the package using the `-e` pip flag 
to ensure it is available in 'editable' mode ([see the docs](https://pip.pypa.io/en/stable/reference/pip_install/)).

```bash
# at the repository root (osd2f/)
pip install -e ./
```

### 3. Install development requirements 

There are additional requirements for development purposes that 
mainly serve to ensure proper formatting and static analysis. Install
them seperately:

```bash
# at the repository root (osd2f/)
pip install -r requirements_dev.txt
```

### 4. Run the code in development mode

While developing, it's probably nice to use development mode *and* set the
log level to DEBUG. You can do so by:

```bash
osd2f -m Development -vvv 
```
The server will now automatically reload when changes are detected. In addition, the settings `yaml` file will be reloaded for each request so
you can quickly iterate on it. 

### javascript

If you are planning to touch the javascript part of the application, you
are recommended to install the npm packages

```bash
npm i --also=dev
```

During development, it's probably nice to have human readable javascript in the
browser (so you can use the build-in debuggers). Use `npm run development` to have webpack watch the javascript files and re-generate a human-readable `main.js` while you work. Once your javascript works well, use `npm run build` to generate the proper minified `main.js` to check in. 


## About fake data

Fake data is part of this repository to demonstrate potential donations. It allows you to play around with data
that on it's service should be similar to real donations when testing your deployment, developing new anonymizes or
visualizations. 

Fake data was generated using the 'faker' package implementation in [scripts/facebook_data_generator.py](../scripts/facebook_data_generator.py), using the command:

```bash
python scripts/facebook_data_generator.py -o mockdata/facebook --overwrite -i 2 -z -tz -t
```

More information about how to use this script, consult the help:

```bash
python scripts/facebook_data_generator.py -h
```

## Code style & checks

There are a number of checks to run in order to guarantee all tests pass, formatting is correct and typing is properly applied. You can run these manually:

```bash
flake8 ./ # formatting analysis
mypy ./ # static analysis
pytest ./ # unittests
```

You can opt to run `black` seperately to apply auto-formatting (`flake8-black` only checks, without corrections).

```bash
black ./
```

Note that most IDEs (e.g. PyCharms, VSCode, ...) allow you to automatically run these commands every time you save, commit or attempt to push the code. We especially advice you to run black on every save. 