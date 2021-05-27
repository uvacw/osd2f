from unittest import TestCase
from unittest.mock import Mock, patch


class test_util_settings_loader(TestCase):
    def test_settings_caching(self):
        disk_load = Mock()
        with patch("osd2f.utils._load_settings_from_disk", disk_load):
            from osd2f.utils import load_upload_settings

            load_upload_settings()
            load_upload_settings()
            self.assertTrue(disk_load.assert_called_once)

    def test_settings_without_caching(self):
        disk_load = Mock()
        with patch("osd2f.utils._load_settings_from_disk", disk_load):
            from osd2f.utils import load_upload_settings

            load_upload_settings(True)
            load_upload_settings(True)
            self.assertTrue(disk_load.call_count == 2)
