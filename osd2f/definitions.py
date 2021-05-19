from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, validator
import pydantic


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


class UploadSettings(BaseModel):
    files: Dict[str, FileSetting]


class BlockTypeEnum(str, Enum):
    jumbotron = "jumbotron"
    twoblockrow = "two_block_row"


class ImagePositionEnum(str, Enum):
    right = "right"
    left = "left"


class ContentButton(BaseModel):
    name: str
    link: str
    label: str


class PageTypeEnum(str, Enum):
    home = "home"
    privacy = "privacy"
    donate = "donate"


class CirclesRowCircle(BaseModel):
    image: str
    title: Optional[str]
    subtitle: Optional[str]


class ContentBlock(BaseModel):
    type: BlockTypeEnum
    id: str
    title: Optional[str]
    lines: List[str]
    buttons: List[ContentButton]
    image: Optional[str]
    image_pos: Optional[ImagePositionEnum]
    circles_row: Optional[List[CirclesRowCircle]]


class ContentPage(BaseModel):
    active: bool
    name: str
    blocks: List[ContentBlock]


class ContentSettings(BaseModel):
    project_title: str
    contact_us: pydantic.EmailStr
    static_pages: Dict[PageTypeEnum, ContentPage]


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
