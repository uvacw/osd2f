import json
import os
from unittest.mock import AsyncMock, patch

from aiounittest.case import AsyncTestCase


class NoAuthConfigTest(AsyncTestCase):
    async def test_noauth(self):
        from osd2f.server import start

        app = start(run=False)
        tc = app.test_client()
        r = await tc.get("/researcher")
        assert r.status_code == 501


class MockMSAL:
    class ConfidentialClientApplication:
        def __init__(self, user: str = None, *args, **kwargs):
            pass

        def initiate_auth_code_flow(self, *args, **kwargs):
            return {"auth_uri": "/researcher"}

        def acquire_token_by_auth_code_flow(self, *args, **kwargs):
            return {
                "id_token_claims": {"preferred_username": "testuser@yourdirectory.com"}
            }


class MSALAuthTest(AsyncTestCase):
    async def test_known_email(self):
        mock_config = {
            "client_id": "f4k3-1D",
            "secret": "53CR37",
            "tenant_id": "73N4N7",
            "allowed_users": "testuser@yourdirectory.com",
        }
        os.environ["MSAL_CONFIG"] = json.dumps(mock_config)

        subMock = AsyncMock(
            return_value=[
                {
                    "db_id": "a",
                    "submission_id": "test_sid",
                    "filename": "testfilename",
                    "n_deleted_across_file": 0,
                    "insert_timestamp": "2020-04-08T23:30",
                    "entry": {},
                }
            ]
        )

        with patch("osd2f.security.microsoft_msal.msal", MockMSAL), patch(
            "osd2f.database.get_submissions", subMock
        ), patch("osd2f.security.microsoft_msal.insert_log", AsyncMock()):
            from osd2f.server import start

            app = start(run=False)
            app.secret_key = "TESTINGSECRET"
            tc = app.test_client()

            # redirect to flow
            r = await tc.get("/researcher")
            assert r.status_code == 302

            # redirect as comming back from microsoft
            r = await tc.get("/researcher")
            assert r.status_code == 302

            # now recognized for login
            r = await tc.get("/researcher")
            assert r.status_code == 200

            # able to download file
            r = await tc.get("/researcher/osd2f_completed_submissions.csv")
            assert r.status_code == 200

    async def test_known_email_of_multiple(self):
        mock_config = {
            "client_id": "f4k3-1D",
            "secret": "53CR37",
            "tenant_id": "73N4N7",
            "allowed_users": "testuser@yourdirectory.com ; anotheruser@yourdirectory.com",
        }
        os.environ["MSAL_CONFIG"] = json.dumps(mock_config)

        subMock = AsyncMock(
            return_value=[
                {
                    "db_id": "a",
                    "submission_id": "test_sid",
                    "filename": "testfilename",
                    "n_deleted_across_file": 0,
                    "insert_timestamp": "2020-04-08T23:30",
                    "entry": {},
                }
            ]
        )

        with patch("osd2f.security.microsoft_msal.msal", MockMSAL), patch(
            "osd2f.database.get_submissions", subMock
        ), patch("osd2f.security.microsoft_msal.insert_log", AsyncMock()):
            from osd2f.server import start

            app = start(run=False)
            app.secret_key = "TESTINGSECRET"
            tc = app.test_client()

            # redirect to flow
            r = await tc.get("/researcher")
            assert r.status_code == 302

            # redirect as comming back from microsoft
            r = await tc.get("/researcher")
            assert r.status_code == 302

            # now recognized for login
            r = await tc.get("/researcher")
            assert r.status_code == 200

            # able to download file
            r = await tc.get("/researcher/osd2f_completed_submissions.csv")
            assert r.status_code == 200

    async def test_unknown_email(self):
        mock_config = {
            "client_id": "f4k3-1D",
            "secret": "53CR37",
            "tenant_id": "73N4N7",
            "allowed_users": "unknown_user@yourdirectory.com",
        }
        os.environ["MSAL_CONFIG"] = json.dumps(mock_config)

        subMock = AsyncMock(
            return_value=[
                {
                    "db_id": "a",
                    "submission_id": "test_sid",
                    "filename": "testfilename",
                    "n_deleted_across_file": 0,
                    "insert_timestamp": "2020-04-08T23:30",
                    "entry": {},
                }
            ]
        )

        with patch("osd2f.security.microsoft_msal.msal", MockMSAL), patch(
            "osd2f.database.get_submissions", subMock
        ), patch("osd2f.security.microsoft_msal.insert_log", AsyncMock()):
            from osd2f.server import start

            app = start(run=False)
            app.secret_key = "TESTINGSECRET"
            tc = app.test_client()

            # redirect to flow
            r = await tc.get("/researcher")
            assert r.status_code == 302

            # redirect as comming back from microsoft,
            # but the email is not accepted
            r = await tc.get("/researcher")
            assert r.status_code == 403

            # login is rejected
            # first by retrying authentication
            r = await tc.get("/researcher")
            assert r.status_code == 302
            # but rejecting the same email
            r = await tc.get("/researcher")
            assert r.status_code == 403

            # unable to download file
            r = await tc.get("/researcher/osd2f_completed_submissions.csv")
            r = await tc.get("/researcher/osd2f_completed_submissions.csv")
            assert r.status_code == 403