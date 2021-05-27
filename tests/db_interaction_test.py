"""Database test files.

We don't want to test our ORM package, so these tests target the convenvience
functions used.
"""
import asyncio
import os
import sqlite3
import time
from unittest.mock import AsyncMock, patch

from aiounittest.case import AsyncTestCase

from osd2f.database import stop_database


class DatabaseStartStopTest(AsyncTestCase):
    async def test_initialize_database(self):
        from osd2f.database import initialize_database

        # we use a file simply because we want to access the same database
        # in the test as in the app context
        db_file = "test_temp"
        db_url = f"sqlite://{db_file}"

        await initialize_database(db_url=db_url)

        c = sqlite3.connect(db_file)

        # check if the submissions table can be queried
        c.execute("SELECT * FROM submissions").fetchall()

        os.remove(db_file)
        os.remove(db_file + "-shm")
        os.remove(db_file + "-wal")

        await stop_database()

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
                n_deleted=2,
                entries=[{"entry": ii, "text": "here"} for ii in range(nentries)],
            )
            for i in range(nfiles)
        ]

        for sub in submissions:
            await insert_submission(sub)

        self.assertEqual(await DBSubmission.all().count(), nfiles * nentries)
        self.assertEqual(
            await DBSubmission.filter(n_deleted=2).count(), nfiles * nentries
        )

        await stop_database()


class UploadSubmissionTest(AsyncTestCase):
    async def test_upload_submission(self):
        from osd2f.definitions import Submission, SubmissionList

        sublist_db_mock = AsyncMock()

        nfiles = 10
        nentries = 10

        submissions = SubmissionList(
            __root__=[
                Submission(
                    submission_id=f"testing-{i}",
                    filename=f"testing_{i}.json",
                    n_deleted=10,
                    entries=[{"entry": ii, "text": "here"} for ii in range(nentries)],
                )
                for i in range(nfiles)
            ]
        )

        with patch("osd2f.server.database.insert_submission_list", sublist_db_mock):
            from osd2f import server

            testclient = server.app.test_client()
            r = await testclient.post("/upload", data=submissions.json())
            assert r.status_code == 200

            sublist_db_mock.assert_called_once_with(submissionlist=submissions)


class LogInsertTest(AsyncTestCase):
    async def test_log_insert(self):
        from osd2f.database import initialize_database, insert_log

        # we use a file simply because we want to access the same database
        # in the test as in the app context
        db_file = "test_temp"
        db_url = f"sqlite://{db_file}"

        await initialize_database(db_url=db_url)

        await insert_log("backend", "INFO", "position")
        await insert_log("backend", "INFO", "position")
        await insert_log("backend", "INFO", "position", "sid_string")
        await insert_log(
            "backend", "INFO", "position", "sid_string2", {"thing": "value"}
        )

        c = sqlite3.connect(db_file)

        # check if the submissions table received the inserts,
        # because they are non-blocking, we'll have to just
        # wait a bit
        r = []
        for i in range(100):
            r = c.execute("SELECT * FROM osd2f_logs").fetchall()
            if len(r) == 4:
                break
            await asyncio.sleep(0.01)

        assert r, ValueError("No(t all) records returned")

        assert (
            len(c.execute("SELECT * FROM osd2f_logs WHERE log_sid IS NULL").fetchall())
            == 2
        )
        assert (
            len(
                c.execute(
                    "SELECT * FROM osd2f_logs WHERE log_sid IS NOT NULL"
                ).fetchall()
            )
            == 2
        )
        assert (
            len(
                c.execute(
                    "SELECT * FROM osd2f_logs WHERE log_entry IS NOT NULL"
                ).fetchall()
            )
            == 1
        )
        c.close()

        os.remove(db_file)
        os.remove(db_file + "-shm")
        os.remove(db_file + "-wal")

        await stop_database()


class LoggerToDBTest(AsyncTestCase):
    async def test_log_to_db(self):
        from osd2f.database import initialize_database, add_database_logging
        from osd2f.logger import logger

        # we use a file simply because we want to access the same database
        # in the test as in the app context
        db_file = "test_temp2"
        db_url = f"sqlite://{db_file}"

        await initialize_database(db_url=db_url)

        logger.setLevel("DEBUG")

        q = add_database_logging()

        logger.debug("seen debug")
        logger.info("seen info")
        logger.warning("seen warning")
        logger.critical("seen critical")

        q.put("stop")

        c = sqlite3.connect(db_file)

        r = []
        for i in range(100):
            r = c.execute("SELECT * FROM osd2f_logs").fetchall()
            if len(r) == 4:
                break
            time.sleep(0.01)

        os.remove(db_file)
        os.remove(db_file + "-shm")
        os.remove(db_file + "-wal")

        await stop_database()
