import base64
import json
import os
from unittest.mock import AsyncMock, patch

from aiounittest.case import AsyncTestCase

from osd2f.server import create_app, stop_database


class NoAuthConfigTest(AsyncTestCase):
    async def test_noauth(self):
        from osd2f.server import create_app

        app = create_app()
        tc = app.test_client()
        r = await tc.get("/researcher")
        assert r.status_code == 501
        await app.shutdown()


class MockMSAL:
    class ConfidentialClientApplication:
        def __init__(self, user: str = None, *args, **kwargs):
            pass

        def initiate_auth_code_flow(self, *args, **kwargs):
            return {"auth_uri": "/login"}

        def acquire_token_by_auth_code_flow(self, *args, **kwargs):
            return {
                "id_token_claims": {"preferred_username": "testuser@yourdirectory.com"}
            }


class MockMSALNoToken:
    class ConfidentialClientApplication:
        def __init__(self, user: str = None, *args, **kwargs):
            pass

        def initiate_auth_code_flow(self, *args, **kwargs):
            return {"auth_uri": "/researcher"}

        def acquire_token_by_auth_code_flow(self, *args, **kwargs):
            return {}


class MSALAuthTest(AsyncTestCase):
    async def test_known_email(self):
        mock_config = {
            "client_id": "f4k3-1D",
            "secret": "53CR37",
            "tenant_id": "73N4N7",
            "allowed_users": "testuser@yourdirectory.com",
            "redirect_url": "localhost:5000",
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

        with patch("osd2f.security.authorization.microsoft_msal.msal", MockMSAL), patch(
            "osd2f.database.get_submissions", subMock
        ), patch("osd2f.security.authorization.microsoft_msal.insert_log", AsyncMock()):
            from osd2f.database import initialize_database, stop_database
            from osd2f.server import create_app

            app = create_app()
            await initialize_database("sqlite://:memory:")
            app.secret_key = "TESTINGSECRET"
            tc = app.test_client()

            # redirect to flow
            r = await tc.get("/researcher")  # , follow_redirects=True)
            assert r.status_code == 302
            assert r.location == "/login"

            r = await tc.get("/login")
            assert r.status_code == 302

            # redirect as comming back from microsoft
            r = await tc.get("/login")
            assert r.status_code == 302

            # now recognized for login
            r = await tc.get("/researcher")
            assert r.status_code == 200

            # able to download file
            r = await tc.get("/researcher/osd2f_completed_submissions.csv")
            assert r.status_code == 200

            await stop_database()

    async def test_known_email_of_multiple(self):
        mock_config = {
            "client_id": "f4k3-1D",
            "secret": "53CR37",
            "tenant_id": "73N4N7",
            "allowed_users": "testuser@yourdirectory.com ;"
            " anotheruser@yourdirectory.com",
            "redirect_url": "localhost:5000",
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

        with patch("osd2f.security.authorization.microsoft_msal.msal", MockMSAL), patch(
            "osd2f.database.get_submissions", subMock
        ), patch("osd2f.security.authorization.microsoft_msal.insert_log", AsyncMock()):
            from osd2f.database import initialize_database, stop_database
            from osd2f.server import create_app

            app = create_app()
            await initialize_database("sqlite://:memory:")
            app.secret_key = "TESTINGSECRET"
            tc = app.test_client()

            # redirect to flow
            r = await tc.get("/login")
            assert r.status_code == 302

            # redirect as comming back from microsoft
            r = await tc.get("/login")
            assert r.status_code == 302

            # now recognized for login
            r = await tc.get("/login")
            assert r.status_code == 200

            # able to download file
            r = await tc.get("/researcher/osd2f_completed_submissions.csv")
            assert r.status_code == 200

            await stop_database()

    async def test_unknown_email(self):
        mock_config = {
            "client_id": "f4k3-1D",
            "secret": "53CR37",
            "tenant_id": "73N4N7",
            "allowed_users": "unknown_user@yourdirectory.com",
            "redirect_url": "localhost:5000",
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

        with patch("osd2f.security.authorization.microsoft_msal.msal", MockMSAL), patch(
            "osd2f.database.get_submissions", subMock
        ), patch("osd2f.security.authorization.microsoft_msal.insert_log", AsyncMock()):
            from osd2f.server import create_app

            app = create_app()
            app.secret_key = "TESTINGSECRET"
            tc = app.test_client()

            # redirect to flow
            r = await tc.get("/login")
            assert r.status_code == 302

            # redirect as comming back from microsoft,
            # but the email is not accepted
            r = await tc.get("/login")
            assert r.status_code == 403

            # login is rejected
            # first by retrying authentication
            r = await tc.get("/login")
            assert r.status_code == 302
            # but rejecting the same email
            r = await tc.get("/login")
            assert r.status_code == 403

            # unable to download file
            r = await tc.get("/login")
            r = await tc.get("/researcher/osd2f_completed_submissions.csv")
            assert r.status_code == 403

    async def test_known_email_app_without_token_access(self):
        mock_config = {
            "client_id": "f4k3-1D",
            "secret": "53CR37",
            "tenant_id": "73N4N7",
            "allowed_users": "testuser@yourdirectory.com",
            "redirect_url": "localhost:5000",
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

        with patch(
            "osd2f.security.authorization.microsoft_msal.msal", MockMSALNoToken
        ), patch("osd2f.database.get_submissions", subMock), patch(
            "osd2f.security.authorization.microsoft_msal.insert_log", AsyncMock()
        ):
            from osd2f.server import create_app

            app = create_app()
            app.secret_key = "TESTINGSECRET"
            tc = app.test_client()

            # redirect to flow
            r = await tc.get("/researcher")
            assert r.status_code == 302
            assert r.location == "/login"

            r = await tc.get("/login")
            assert r.status_code == 302

            # redirect as comming back from microsoft
            r = await tc.get("/login")
            assert r.status_code == 500

            await stop_database()


class BasicAuthTest(AsyncTestCase):
    async def test_basic_auth(self):
        import osd2f.security

        with patch.dict(
            osd2f.security.os.environ,
            {"OSD2F_BASIC_AUTH": "testuser;testpassword", "OSD2F_SECRET": "testsecret"},
            clear=True,
        ):

            app = create_app()
            await app.startup()
            app.secret_key = "TESTINGSECRET"
            tc = app.test_client()

            r = await tc.get("/researcher")
            assert r.status_code == 302

            r = await tc.get("/login")
            assert r.status_code == 401

            encoded_auth = base64.b64encode(b"testuser:testpassword")
            r = await tc.open(
                "/login", headers={"Authorization": f"Basic {encoded_auth.decode()}"}
            )
            assert r.status_code == 302

            r = await tc.get("/researcher")
            assert r.status_code == 200

            await app.shutdown()
