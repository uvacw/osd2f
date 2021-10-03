import os
from unittest.async_case import IsolatedAsyncioTestCase

from osd2f.server import create_app


class TestPasswordProtectedDownloads(IsolatedAsyncioTestCase):
    async def test_password_protected_downloads(self):
        from osd2f.security.authorization import USER_FIELD

        testapp = create_app(
            data_password_override="testpassword", app_secret_override="testsecret"
        )
        await testapp.startup()

        # set placeholder to trigger authorization
        os.environ["MSAL_CONFIG"] = "placeholder"

        tc = testapp.test_client()

        # set cookie to avoid real MSAL flow
        async with tc.session_transaction() as session:
            session[USER_FIELD] = "testuser"

        r = await tc.get("/researcher/osd2f_completed_submissions.json.zip")
        assert r.status_code == 200

        os.environ.pop("MSAL_CONFIG")

        await testapp.shutdown()
