import argparse
import asyncio
import json
import logging

from osd2f import config

import yaml

from .config import Testing
from .database import initialize_database, stop_database
from .logger import logger
from .server import create_app, start_app

LOGFORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

parser = argparse.ArgumentParser(
    prog="OSD2F webserver", usage="Start the webserver and collect data donations."
)

parser.add_argument(
    "-m",
    "--mode",
    action="store",
    default="Testing",
    help="Specify the mode to run in, defaults to 'Testing'",
    choices=[
        d
        for d in dir(config)
        if not d.startswith("_") and d[0] == d[0].upper() and d != "Config"
    ],
)
parser.add_argument(
    "-v",
    "--verbose",
    action="count",
    default=0,
    help="Verbosity of logging output, defaults to default=CRITICAL, "
    "v=WARNING, vv=INFO, vvv=DEBUG",
)

parser.add_argument(
    "-db",
    "--database-url",
    type=str,
    help="The database URL to use, overrides the `OSD2F_DB_URL` environment variable.",
)

parser.add_argument(
    "--secret",
    type=str,
    help="Overrides `OSD2F_SECRET` environment variable with"
    " an application secret for session security.",
)

parser.add_argument(
    "--download-password",
    type=str,
    help="Overrides `OSD2F_DATA_PASSWORD` environment variable "
    "for researcher download file password protection.",
)

parser.add_argument(
    "--entry-encryption-secret",
    type=str,
    help="Overrides `OSD2F_ENTRY_SECRET` environment variable. "
    "Encryption key for per-entry encryption/decryption for writing/reading "
    "from database.",
)

parser.add_argument(
    "--generate-current-config",
    type=str,
    help="Path to put an current content configuration YAML file.",
)

parser.add_argument(
    "-cc",
    "--content-configuration",
    type=str,
    help="A content configuration YAML file",
)

parser.add_argument(
    "--dry-run",
    action="store_true",
    help="test whether endpoints provide 200 code responses,"
    " just to make sure nothing broke.",
)

parser.add_argument(
    "--entry-decrypt-on-read-disabled",
    action="store_true",
    default=False,
    help="Keep entries downloaded through the researcher interface encrypted. "
    "Overrides the `OSD2F_ENTRY_DECRYPT_DISABLE` ENV variable",
)


def parse_and_run():
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

    logging.basicConfig(format=LOGFORMAT, level="WARNING")
    logger.setLevel(level=level)

    logger.debug(
        "If you see this, you are running with debug logging. "
        "DO NOT DO THIS IN PRODUCTION."
    )

    if args.content_configuration:
        import osd2f.utils

        osd2f.utils.DISK_CONTENT_CONFIG_PATH = args.content_configuration

    app = create_app(
        mode=args.mode,
        database_url_override=args.database_url,
        entry_secret_override=args.entry_encryption_secret,
        entry_decrypt_disable=args.entry_decrypt_on_read_disabled,
    )
    if not args.dry_run and not args.generate_current_config:
        start_app(app)

    elif args.generate_current_config:
        from osd2f.utils import load_content_settings

        asyncio.run(app.startup())
        settings = asyncio.run(load_content_settings(use_cache=False))
        with open(args.generate_current_config, "w") as outputfile:
            yaml.dump(settings.dict(by_alias=True), outputfile)
        asyncio.run(app.shutdown())

    else:
        asyncio.run(initialize_database(Testing.DB_URL))
        tp = app.test_client()
        assert asyncio.run(tp.get("/")).status_code == 200
        assert asyncio.run(tp.get("/privacy")).status_code == 200
        assert asyncio.run(tp.get("/upload")).status_code == 200
        assert asyncio.run(tp.get("/static/js/main.js")).status_code == 200
        assert asyncio.run(tp.get("/adv_anonymize_file")).status_code == 405
        assert (
            asyncio.run(
                tp.post(
                    "/adv_anonymize_file",
                    data=json.dumps(
                        {
                            "filename": "fn",
                            "submission_id": "sid",
                            "entries": [{}],
                            "n_deleted": 0,
                        }
                    ),
                )
            ).status_code
            == 200
        )
        asyncio.run(stop_database())
