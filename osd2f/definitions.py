from typing import Any, Dict, List, Optional

from pydantic import BaseModel, validator


class Submission(BaseModel):
    submission_id: str
    filename: str
    n_deleted: int
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


class MSALConfiguration(BaseModel):
    tenant_id: str
    client_id: str
    secret: str
    allowed_users: str
    redirect_url: str

    authority: Optional[str] = None
    scope: List[str] = ["User.Read"]

    @validator("authority", pre=True, always=True)
    def set_authority(cls, v, *, values, **kwargs):
        return f"https://login.microsoftonline.com/{values['tenant_id']}"
