import io

import pyzipper


def string_to_zipfile(file_content: io.StringIO, filename: str, password: str) -> bytes:
    """Write a string body to a file in an encrypted zip archive."""
    zipio = io.BytesIO()
    with pyzipper.AESZipFile(zipio, "w", encryption=pyzipper.WZ_AES) as zipfile:
        zipfile.setpassword(password.encode())
        zipfile.writestr(filename, file_content.getvalue())
    return zipio.getvalue()
