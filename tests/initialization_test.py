from unittest import TestCase, mock


class InitializationTests(TestCase):
    def test_production_init_without_secret(self):
        from osd2f.server import start, config

        config.Production.SECRET_KEY = None

        self.assertRaises(Exception, start, mode="Production")

    def test_production_init_with_secret(self):
        # must be set before import
        from osd2f.server import app, config, start

        config.Production.SECRET_KEY = "not none"

        app.run = mock.Mock()
        start(mode="Production")
