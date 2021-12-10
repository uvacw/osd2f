# Adding new anonymizer functions

This guide explains how to add anonymization functions to the codebase. You will need
Python skill to create a new anonymizer.

## What are anonymizers

Simply put, anonymizers are functions that run on the server *before* data is collected. They 
are meant for more complex processing of submission entries for privacy protecting purposes. For 
instance, they could be named entity recognition functions that filter out personal names using
(pretrained) machine learning models. 

Anonymizers are run server-side **before consent is given** and should never store data on disk. 

## How do anonymizers work

When a user selects files to upload, the containing entries are parsed. This parsing removes fields
that are not on the whitelist, and 'flattens' the dictionaries using `.` notation. After this client-side
parsing, the entries are send to the server where the configured anonymizers are called.

For each file that has a configured anonymizer, each entry is provided to that anonymizer function. The
anonymizer function should return the entry after changing it's contents. These entries are then returned
to the client for respondents to inspect and provide consent on the real upload. 

## Creating a new anonymizer

You can create an anonymizer by adding a file to the `osd2f/anonymizers` directory, importing it in the 
`osd2f/anonymizers/__init__.py` file and configuring the use of the anonymizer in the upload settings 
YAML file used for your deployment. 

### Writing a new anonymizer

Anonymizers should have this signature: 

```python
async def your_anonymizer(
    entry: typing.Dict[str, typing.Any], argument: str = "optional_string_argument"
) -> typing.Dict[str, typing.Any]
```

For example, we'll implement an anonymizer that goes through a text and removes any word after a 
given substring:

```python
# in new file: osd2f/anonymizers/nextword_anonymizer.py
from typing import Any, Dict

async def nextword_anonymizer(entry: Dict[str,Any], substring: str):
    
    redacted_entry = {}
    for field, value in entry.items():
        # keep field values that are not a string as-is
        # in the redacted entry
        if type(value)!=str:
            redacted_entry[field] = value
            continue
        
        # naively split the value on spaces
        # and keep the words that do not come after
        # the substring
        previous_token = ""
        new_value = []
        for token in value.split(" "):
            if previous_token!=substring:
                new_value.append(token)
            else:
                new_value.append("<redacted>")
            previous_token = token

        redacted_entry[field] = " ".join(new_value)
    
    # make sure to return the redacted version of the entry
    return redacted_entry

```

You can test the function:

```python
from osd2f.anonymizers.nextword_anonymizer import nextword_anonymizer

fake_entry = {
    "text" : "mr Darcy was unamused, but so was mr bennet"
}

await nextword_anonymizer(fake_entry, "mr")

```
outputs: 
``` {'text': 'mr <redacted> was unamused, but so was mr <redacted>'} ```


### Adding the anonymizer to imports

For OSD2F to recognize the new anonymizer, it needs to be added to the `osd2f/anonymizers/__init__.py` file, like so:

```python
# in osd2f/anonymizers/__init__.py 
import re
import typing

from .sample_platform import redact_text
from .nextword_anonymizer import nextword_anonymizer # <- import the new anonymizer function
from ..definitions import Submission, SubmissionList, UploadSettings
from ..logger import logger

options: typing.Dict[str, typing.Callable[[typing.Dict, str], typing.Awaitable]] = {
    redact_text.__name__: redact_text,  # noqa
    nextword_anonymizer.__name__ : nextword_anonymizer # noqa <- add it to the options
}

...rest of the file...
```


### Configuring settings to use this anonymizer

Let's try to use this new anonymizer. First, we create an upload settings file:

```yaml
# in osd2f/settings/default_upload_settings.yaml
files:
  example.json:
    anonymizers:
      - nextword_anonymizer : "mr"
    accepted_fields:
      - text
      - title
      - number
```

Then we create a file to donate called `example.json`:

```json
[
  {
    "title": "mr Frogs day out",
    "text": "mr Frog was driving on the windy road towards mr Toad",
    "number": 100,
    "other": "is not on the whitelist"
  }
]
```

We start the OSD2F platform:

```bash
OSD2F_SECRET=secret \                                                              
OSD2F_ENTRY_SECRET=TESTSECRET \
OSD2F_MODE=Development \
osd2f -vvv
```

We upload our `example.json` file on the [upload page](http://localhost:5000/upload)

Press the `inspect & edit` button and you will see the redacted result in the table! 