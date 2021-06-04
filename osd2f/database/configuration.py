import typing

from tortoise import fields
from tortoise.models import Model

from ..definitions import ContentSettings, UploadSettings


class DBConfigurationBlobs(Model):
    id = fields.IntField(pk=True)
    insert_timestamp = fields.DatetimeField(auto_now_add=True)
    insert_user = fields.CharField(index=True, max_length=150, null=False)
    config_type = fields.CharField(index=True, max_length=50, null=False)
    config_blob = fields.JSONField(null=False)

    class Meta:
        table = "osd2f_config"


async def get_content_config() -> typing.Optional[DBConfigurationBlobs]:
    config_item = (
        await DBConfigurationBlobs.filter(config_type="content")
        .order_by("-insert_timestamp")
        .first()
    )
    return config_item


async def set_content_config(user: str, content: ContentSettings):
    await DBConfigurationBlobs.create(
        insert_user=user, config_type="content", config_blob=content.json()
    )


async def set_upload_config(user: str, content: UploadSettings):
    await DBConfigurationBlobs.create(
        insert_user=user, config_type="upload", config_blob=content.json()
    )
