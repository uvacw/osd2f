from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class Submission(BaseModel):
    submission_id: str
    filename: str
    entries: List[Dict[str, Any]]


class SubmissionList(BaseModel):
    """Basically, a list of file submissions as one List."""

    __root__: List[Submission]


class FileSetting(BaseModel):
    in_key: Optional[str]
    accepted_fields: List[str]
    anonymizers: Optional[List[Dict[str, str]]]


class Settings(BaseModel):
    files: Dict[str, FileSetting]
