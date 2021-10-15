import datetime
import importlib
from unittest.mock import AsyncMock, Mock, patch

from aiounittest.case import AsyncTestCase

from osd2f.database.submissions import (
    get_submissions,
    insert_submission,
    insert_submission_list,
)


class ConfigTest(AsyncTestCase):
    def test_cli_override(self):
        from osd2f.server import create_app

        m = Mock()
        with patch("osd2f.server.SecureEntry.set_secret", m):
            create_app(entry_secret_override="entry_override")
            m.assert_called_once_with(secret="entry_override")

    def test_env_var_use(self):
        import osd2f.config
        from osd2f.server import create_app

        m = Mock()
        with patch(
            "osd2f.config._os.environ", {"OSD2F_ENTRY_SECRET": "another_secret"}
        ), patch("osd2f.server.SecureEntry.set_secret", m):
            # force reload to trigger new processing of
            # env variables
            importlib.reload(osd2f.config)

            create_app()
            m.assert_called_once_with(secret="another_secret")

    def test_env_var_override(self):
        import osd2f.config
        from osd2f.server import create_app

        m = Mock()
        with patch(
            "osd2f.config._os.environ", {"OSD2F_ENTRY_SECRET": "another_secret"}
        ), patch("osd2f.server.SecureEntry.set_secret", m):
            # force reload to trigger new processing of
            # env variables
            importlib.reload(osd2f.config)

            create_app(entry_secret_override="entry_override")
            m.assert_called_once_with(secret="entry_override")


class SecureEntryTest(AsyncTestCase):
    def test_without_secret(self):
        from osd2f.security.entry_encryption.secure_entry_singleton import SecureEntry

        SecureEntry.set_secret("")

        entry = {"stuff": "is unsafe"}
        unencrypted = SecureEntry.write_entry_field(entry.copy())

        self.assertEqual(entry, unencrypted)

        loaded_entry = SecureEntry.read_entry_field(entry.copy())
        self.assertEqual(entry, loaded_entry)

    def test_with_secret(self):
        from osd2f.security.entry_encryption.secure_entry_singleton import SecureEntry

        SecureEntry.set_secret("secret")
        entry = {"stuff": "is safe"}

        encrypted = SecureEntry.write_entry_field(entry.copy())
        self.assertIsNotNone(encrypted.get("encrypted"))
        self.assertEqual(entry, SecureEntry.read_entry_field(encrypted))

    def test_consistent_key(self):
        from osd2f.security.entry_encryption.secure_entry_singleton import SecureEntry

        m = {"thing": "to encrypt"}
        SecureEntry.set_secret("secret")
        e = SecureEntry.write_entry_field(m.copy())
        SecureEntry.set_secret("secret")
        m2 = SecureEntry.read_entry_field(e)

        self.assertEqual(m, m2)


class DatabaseOperationsTest(AsyncTestCase):
    async def test_insert_submission(self):
        from osd2f.definitions.submissions import Submission

        class MockSecureEntry:
            pass

        MockSecureEntry.read_entry_field = Mock()
        MockSecureEntry.write_entry_field = Mock()
        with patch("osd2f.database.submissions.SecureEntry", MockSecureEntry), patch(
            "osd2f.database.DBSubmission.create", AsyncMock()
        ):
            s = Submission(
                submission_id="id",
                filename="file",
                entries=[{"thing": "here"}],
                n_deleted=0,
            )
            await insert_submission(s)
            MockSecureEntry.write_entry_field.assert_called_once_with(s.entries[0])

    async def test_insert_submission_list(self):
        from osd2f.definitions.submissions import Submission, SubmissionList

        class MockSecureEntry:
            pass

        MockSecureEntry.read_entry_field = Mock()
        MockSecureEntry.write_entry_field = Mock()

        async def mock_bulk_create(objects):
            for i in objects:
                pass

        with patch("osd2f.database.submissions.SecureEntry", MockSecureEntry), patch(
            "osd2f.database.DBSubmission.bulk_create", mock_bulk_create
        ):
            s = Submission(
                submission_id="id",
                filename="file",
                entries=[{"thing": "here"}],
                n_deleted=0,
            )
            await insert_submission_list(SubmissionList(__root__=[s]))
            MockSecureEntry.write_entry_field.assert_called_once_with(s.entries[0])

    async def test_get_submission(self):

        from osd2f.database.submissions import DBSubmission

        class MockSecureEntry:
            pass

        s = DBSubmission(
            id=5,
            submission_id="id",
            filename="file",
            entry={"thing": "here"},
            n_deleted=0,
            insert_timestamp=datetime.datetime.now(),
            update_timestamp=datetime.datetime.now(),
        )

        MockSecureEntry.read_entry_field = Mock(return_value=s)
        MockSecureEntry.write_entry_field = Mock()

        DBSubmission.all = AsyncMock(return_value=[s])
        with patch("osd2f.database.submissions.SecureEntry", MockSecureEntry), patch(
            "osd2f.database.DBSubmission.all", AsyncMock(return_value=[s])
        ):

            await get_submissions()
            MockSecureEntry.read_entry_field.assert_called_once()
