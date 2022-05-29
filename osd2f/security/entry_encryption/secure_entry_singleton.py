import base64
import json
import random
from typing import Any, Dict

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


from ...logger import logger


class SecureEntry:

    __encryption_secret: bytes = b""
    __decrypt_on_read: bool = True

    @classmethod
    def set_secret(cls, secret: str):
        if not secret:
            cls.__encryption_secret = b""
        else:
            cls.__encryption_secret = cls.__create_key(secret.encode())

    @classmethod
    def decrypt_on_read(cls, must_decrypt_on_read: bool):
        cls.__decrypt_on_read = must_decrypt_on_read

    @classmethod
    def write_entry_field(cls, entry_field: Dict[str, Any]) -> Dict[str, Any]:
        if not cls.__encryption_secret:
            return entry_field
        f = Fernet(cls.__encryption_secret)
        return {"encrypted": f.encrypt(json.dumps(entry_field).encode()).decode()}

    @classmethod
    def read_entry_field(cls, entry_field: Dict[str, Any]) -> Dict[str, Any]:
        if not cls.__encryption_secret or not cls.__decrypt_on_read:
            return entry_field
        encrypted_content = entry_field.get("encrypted")

        if not encrypted_content:
            logger.warning(
                "Entry encryption was set, but an unencrypted " "entry was retrieved!"
            )
            return entry_field
        f = Fernet(cls.__encryption_secret)
        content = f.decrypt(encrypted_content.encode())
        return json.loads(content.decode())

    @staticmethod
    def __create_key(password: bytes) -> bytes:
        random.seed(len(password))
        salt = bytes(random.randint(0, 10**6))
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=320_000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
