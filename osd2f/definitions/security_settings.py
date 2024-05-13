from typing import List, Optional

from pydantic import BaseModel, field_validator


class MSALConfiguration(BaseModel):
    tenant_id: str
    client_id: str
    secret: str
    allowed_users: str
    redirect_url: Optional[str]

    authority: Optional[str] = None
    scope: List[str] = ["User.Read"]

    @field_validator("authority", mode="before", check_fields=True)
    def set_authority(cls, v, *, values, **kwargs):
        return f"https://login.microsoftonline.com/{values['tenant_id']}"
