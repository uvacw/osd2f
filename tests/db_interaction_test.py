"""Database test files.

We don't want to test our ORM package, so these tests target the convenvience
functions used.
"""
import os

from aiounittest.case import AsyncTestCase
from unittest.mock import AsyncMock, patch

import sqlite3


class DatabaseStartStopTest(AsyncTestCase):
    async def test_initialize_database(self):
        from osd2f.database import initialize_database

        # we use a file simply because we want to access the same database
        db_file = "test_temp"
        db_url = f"sqlite://{db_file}"

        await initialize_database(db_url=db_url)

        c = sqlite3.connect(db_file)

        # check if the submissions table can be queried
        c.execute("SELECT * FROM submissions").fetchall()

        os.remove(db_file)
        os.remove(db_file + "-shm")
        os.remove(db_file + "-wal")

    async def test_stop_database(self):
        close_mock = AsyncMock()
        with patch("tortoise.Tortoise.close_connections", close_mock):
            from osd2f.database import stop_database

            await stop_database()
            self.assertTrue(await close_mock.is_called())


class DatabaseInsertTest(AsyncTestCase):
    async def test_insert_submission(self):
        from osd2f.config import Testing
        from osd2f.definitions import Submission
        from osd2f.database import (
            DBSubmission,
            insert_submission,
            initialize_database,
            stop_database,
        )

        await initialize_database(Testing.DB_URL)

        nfiles = 10
        nentries = 10

        submissions = [
            Submission(
                submission_id=f"testing-{i}",
                filename=f"testing_{i}.json",
                entries=[{"entry": ii, "text": "here"} for ii in range(nentries)],
            )
            for i in range(nfiles)
        ]

        for sub in submissions:
            await insert_submission(sub)

        self.assertEqual(await DBSubmission.all().count(), nfiles * nentries)

        await stop_database()