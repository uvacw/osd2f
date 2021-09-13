import importlib
import os
from unittest import TestCase
from unittest.mock import Mock, patch


class CreateAppTest(TestCase):
    def test_env_var_config(self):
        test_env_vars = {
            "OSD2F_DB_URL": "testdb",
            "OSD2F_SECRET": "testsecret",
            "OSD2F_DATA_PASSWORD": "datapassword",
        }
        old_env = os.environ.copy()
        os.environ.update(test_env_vars)
        import osd2f.config

        # force reload to trigger new processing of
        # env variables
        importlib.reload(osd2f.config)

        from osd2f.server import create_app

        app = create_app(mode="Production")

        assert app.config["DB_URL"] == "testdb"
        assert app.config["SECRET_KEY"] == "testsecret"
        assert app.config["DATA_PASSWORD"] == "datapassword"

        # reset to old environment
        os.environ = old_env
        importlib.reload(osd2f.config)

    def test_ovveride_var_config(self):
        test_env_vars = {
            "OSD2F_DB_URL": "testdb",
            "OSD2F_SECRET": "testsecret",
            "OSD2F_DATA_PASSWORD": "datapassword",
        }
        old_env = os.environ.copy()
        os.environ.update(test_env_vars)
        import osd2f.config

        # force reload to trigger new processing of
        # env variables
        importlib.reload(osd2f.config)

        from osd2f.server import create_app

        app = create_app(
            mode="Production",
            database_url_override="override_url",
            app_secret_override="override_secret",
            data_password_override="override_datapassword",
        )

        assert app.config["DB_URL"] == "override_url"
        assert app.config["SECRET_KEY"] == "override_secret"
        assert app.config["DATA_PASSWORD"] == "override_datapassword"

        # reset to old environment
        os.environ = old_env
        importlib.reload(osd2f.config)

    def test_overide_var_translation(self):

        mock_translate_value = Mock()
        with patch("osd2f.server.security.translate_value", mock_translate_value):
            from osd2f.server import create_app

            create_app(
                mode="Production",
                database_url_override="override_url",
                app_secret_override="override_secret",
                data_password_override="override_datapassword",
            )
            mock_translate_value.assert_called_with("override_url")

        mock_translate_value = Mock()
        with patch("osd2f.server.security.translate_value", mock_translate_value):
            from osd2f.server import create_app

            create_app(
                mode="Production",
                app_secret_override="override_secret",
                data_password_override="override_datapassword",
            )
            mock_translate_value.assert_called_with("override_secret")

        mock_translate_value = Mock()
        with patch("osd2f.server.security.translate_value", mock_translate_value):
            from osd2f.server import create_app

            create_app(
                mode="Production",
                data_password_override="override_datapassword",
                app_secret_override="tempsecret",
            )
            mock_translate_value.assert_called_with("tempsecret")
