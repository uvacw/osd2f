# Development

## Installation for development

You can install this Python Package for local development purposes. To do 
so, we *strongly* advice using a virtual environment context. 

##### Example using the popular [anaconda distribution of python](https://www.anaconda.com/)

```bash 
conda create -n osd2f python=3.9 # only required once
conda activate osd2f # run at the start of each osd2f development session
```

#### Setting up 

For development purposes, you should install the package using the `-e` pip flag 
to ensure it is available in 'editable' mode ([see the docs](https://pip.pypa.io/en/stable/reference/pip_install/)).

```bash
# at the repository root (OSD2F/)
pip install -e backend/
```

There are additional requirements for development purposes that 
mainly serve to ensure proper formatting and static analysis. Install
them seperately:

```bash
pip install -r requirements_dev.txt
```

## Code style & checks

There are a number of checks to run in order to guarantee all 
tests pass, formatting is correct and typing is properly applied. 
You can run these manually:

```bash
flake8 ./ # formatting analysis
mypy ./ # static analysis
pytest ./ # unittests
```

You can opt to run `black` seperately to apply auto-formatting (`flake8-black` only checks, without corrections).

```bash
black backend/
```

Note that most IDEs (e.g. PyCharms, VSCode, ...) allow you to automatically run these commands every time
you save, commit or attempt to push the code. We especially advice you to run black on every save. 