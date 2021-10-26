from typing import Any, Dict, List

from pydantic import BaseModel


class Submission(BaseModel):
    submission_id: str
    filename: str
    n_deleted: int
    entries: List[Dict[str, Any]]


class OutputSubmission(BaseModel):
    """Submissions as downloaded per-record."""

    db_id: int
    submission_id: str
    filename: str
    n_deleted_across_file: int
    insert_timestamp: str
    entry: Dict[str, Any]


class EncryptedEntry(BaseModel):
    encrypted: str


class EncryptedSubmission(BaseModel):
    """Matches the downloaded submission format based on the database schema."""

    submission_id: str
    filename: str
    n_deleted_across_file: int
    entry: EncryptedEntry


class SubmissionList(BaseModel):
    """Submissions as send from the webbrowser.
    Basically, a list of file submissions as one List."""

    __root__: List[Submission]
