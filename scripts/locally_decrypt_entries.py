"""Decrypts downloaded submissions

Some OSD2F distributions are configured to keep
entries encrypted on download. This script locally
decrypts these entries, provided you have access to
the entry encryption secret.

Usage:

python scripts/locally_decrypt_entries.py -h

"""
import argparse
import logging
import pathlib

from osd2f.logger import logger
from osd2f.security import translate_value
from osd2f.security.entry_encryption.file_decryption import decrypt_file
from osd2f.security.entry_encryption.secure_entry_singleton import SecureEntry

parser = argparse.ArgumentParser(description=__doc__)

parser.add_argument(
    "-v",
    "--verbose",
    action="count",
    default=0,
    help="Verbosity of logging output, defaults to default=CRITICAL, "
    "v=WARNING, vv=INFO, vvv=DEBUG",
)
parser.add_argument("input_file", help="The file of submissions to decrypt.")
parser.add_argument("output_file", help="The file to write decrypted submissions to")

parser.add_argument(
    "secret",
    help="The encryption secret, should be the same "
    "as the secret used to configure the server. "
    "May be a reference to a supported secret store such as Azure KeyVault",
)


def run_script():
    args = parser.parse_args()

    if args.verbose == 0:
        level = logging.CRITICAL
    elif args.verbose == 1:
        level = logging.WARNING
    elif args.verbose == 2:
        level = logging.INFO
    elif args.verbose == 3:
        level = logging.DEBUG
    else:
        print("UNKNOWN LOGLEVEL SPECIFIED")
        level = logging.NOTSET

    logger.setLevel(level=level)

    secret = translate_value(args.secret)
    SecureEntry.set_secret(secret)

    input_path = pathlib.Path(args.input_file)
    output_path = pathlib.Path(args.output_file)

    touched_entries = decrypt_file(input_path=input_path, output_path=output_path)

    logger.info(
        f"Done decrypting {touched_entries} entries from {input_path} to {output_path}"
    )


if __name__ == "__main__":
    run_script()
