from unittest import TestCase, mock


class InitializationTests(TestCase):
    def test_production_init_without_secret(self):
        from osd2f.server import create_app, config

        config.Production.SECRET_KEY = None

        self.assertRaises(Exception, create_app, mode="Production")

    def test_production_init_without_database(self):
        from osd2f.server import create_app, config

        config.Production.SECRET_KEY = "not none"

        self.assertRaises(Exception, create_app, mode="Production")

    def test_production_init_with_secret_and_db(self):
        # must be set before import
        from osd2f.server import app, config, create_app

        config.Production.SECRET_KEY = "not none"
        config.Production.DB_URL = "sqlite:memory"

        app.run = mock.Mock()
        create_app(mode="Production")
        config.Production.DB_URL = None
