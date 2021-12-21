"""tests:
 - config submitted to db
 - correct db vs dsk choice with cache
 - correct db vs dsk choice without cache
 - app config DEBUG in content call
 - app config non-DEBUG in content call
 - static pages take arbitrary content
"""
import os
from unittest.mock import AsyncMock, Mock, patch

from aiounittest.case import AsyncTestCase

from osd2f.definitions import (
    ConsentPopup,
    ContentBlock,
    ContentPage,
    ContentSettings,
    PreviewComponent,
    UploadBox,
    UploadPage,
)

fake_settings = ContentSettings(
    project_title="test project_title",
    contact_us="test@case.nl",
    static_pages={
        "home": ContentPage(
            active=True,
            name="testpage",
            blocks=[ContentBlock(type="two_block_row", id="tb", buttons=[], lines=[])],
        ),
        "privacy": ContentPage(active=True, name="testprivacypage", blocks=[]),
        "donate": ContentPage(active=False, name="testdonatepage", blocks=[]),
    },
    upload_page=UploadPage(
        blocks=[
            ContentBlock(
                type="two_block_row", id="utb", buttons=[], lines=["one", "two"]
            )
        ],
        upload_box=UploadBox(
            header="upload box header test",
            explanation=["explanation test 1", "explanation test 2"],
        ),
        thanks_text="thanks_text_test",
        file_indicator_text="file indicator test",
        processing_text="proces",
        empty_selection="no allowed files selected",
        donate_button="donate button test",
        inspect_button="inspect_button_test",
        preview_component=PreviewComponent(
            entries_in_file_text="entries in file test",
            title="preview component title test",
            explanation=["explanation point test"],
            previous_file_button="prev file button test",
            next_file_button="next file button test",
            remove_rows_button="remove rows button test",
            search_prompt="search prompt test",
            search_box_placeholder="search box placeholder test",
        ),
        consent_popup=ConsentPopup(
            title="consent popup title test",
            lead="consent lead test",
            points=["consent points test"],
            end_text="end text test",
            decline_button="decline buttone test",
            accept_button="accept button test",
        ),
    ),
)


class ContentConfigurationTest(AsyncTestCase):
    async def test_config_load_database_side_effect(self):
        get_content_config_mock = AsyncMock(return_value=None)
        set_content_config_mock = AsyncMock()
        yaml_load_mock = Mock(return_value=fake_settings.dict())

        with patch("osd2f.utils.get_content_config", get_content_config_mock), patch(
            "osd2f.utils.set_content_config", set_content_config_mock
        ), patch("osd2f.utils.yaml.safe_load", yaml_load_mock):
            from osd2f.utils import load_content_settings

            await load_content_settings(use_cache=False)

            get_content_config_mock.assert_called_once()
            set_content_config_mock.assert_called_with(
                user="default", content=fake_settings
            )

    async def test_config_load_with_cache(self):
        get_content_config_mock = AsyncMock(return_value=None)
        set_content_config_mock = AsyncMock()
        yaml_load_mock = Mock(return_value=fake_settings.dict())

        with patch("osd2f.utils.get_content_config", get_content_config_mock), patch(
            "osd2f.utils.set_content_config", set_content_config_mock
        ), patch("osd2f.utils.yaml.safe_load", yaml_load_mock):
            import osd2f.utils
            from osd2f.utils import load_content_settings

            # clear the global var used to cache results
            osd2f.utils.DISK_CONFIG_VERSION = ""

            await load_content_settings(use_cache=True)
            settings = await load_content_settings(use_cache=True)

            # despite two calls to `load_content_settings`
            # the `yaml.safe_load` function should
            # only be called once (instead, the cache is used)
            yaml_load_mock.assert_called_once()

            assert settings == fake_settings

    async def test_config_load_without_cache(self):
        get_content_config_mock = AsyncMock(return_value=None)
        set_content_config_mock = AsyncMock()
        yaml_load_mock = Mock(return_value=fake_settings.dict())

        with patch("osd2f.utils.get_content_config", get_content_config_mock), patch(
            "osd2f.utils.set_content_config", set_content_config_mock
        ), patch("osd2f.utils.yaml.safe_load", yaml_load_mock):
            import osd2f.utils
            from osd2f.utils import load_content_settings

            # clear the global var used to cache results
            osd2f.utils.DISK_CONFIG_VERSION = ""

            await load_content_settings(use_cache=False)
            settings = await load_content_settings(use_cache=False)

            # with use_cache set to `False`, we expect the
            # disk to be read twice
            yaml_load_mock.call_count == 2

            assert settings == fake_settings

    async def test_app_config_testing(self):
        load_content_settings_mock = AsyncMock(return_value=fake_settings)

        with patch(
            "osd2f.server.utils.load_content_settings", load_content_settings_mock
        ):
            from osd2f.server import create_app

            app = create_app()
            await app.startup()
            c = app.test_client()
            await c.get("/")

            load_content_settings_mock.assert_called_with(use_cache=True)
            await app.shutdown()

    async def test_app_config_production(self):
        load_content_settings_mock = AsyncMock(return_value=fake_settings)

        with patch(
            "osd2f.server.utils.load_content_settings", load_content_settings_mock
        ):
            from osd2f.server import create_app

            app = create_app(mode="Development")
            await app.startup()
            c = app.test_client()
            await c.get("/")

            load_content_settings_mock.assert_called_with(use_cache=False)
            await app.shutdown()

    async def test_content_rendering(self):
        load_content_settings_mock = AsyncMock(return_value=fake_settings)

        with patch(
            "osd2f.server.utils.load_content_settings", load_content_settings_mock
        ):
            from osd2f.server import create_app

            app = create_app(mode="Development")
            await app.startup()
            c = app.test_client()
            homepage = await c.get("/")
            body = await homepage.get_data(as_text=True)

            expected_present = ["testpage", "two_block_row", "testprivacypage"]
            for snippet in expected_present:
                assert body.find(snippet)

            expected_absent = ["testdonatepage"]
            for snippet in expected_absent:
                assert body.find(snippet) <= 0

            upload_page = await c.get("/upload")
            body = await upload_page.get_data(as_text=True)

            expected_present = [
                "one",
                "two",
                "upload box header test" "thanks_text_test",
                "explanation test 1",
                "explanation test 2",
                "file indicator test",
                "no allowed files selected",
                "proces",
                # test whether the content settings obj is injected
                fake_settings.json(),
            ]
            for snippet in expected_present:
                assert body.find(snippet)

            await app.shutdown()

    def test_cli_content_file_generation(self):
        from osd2f.cli import parse_and_run
        import osd2f.utils

        import copy
        import sys
        import yaml

        assert osd2f.utils.DISK_CONTENT_CONFIG_PATH.find(
            "default_content_settings.yaml"
        )

        test_file_path = "content_config_file_test.yaml"
        sargv = copy.copy(sys.argv)

        sys.argv = ["", "--dry-run", "--generate-current-config", test_file_path]
        parse_and_run()

        assert len(open(test_file_path).read()) > 0

        sys.argv = sargv
        ContentSettings.parse_obj(yaml.safe_load(open(test_file_path)))
        os.remove(test_file_path)

    def test_cli_content_file_override(self):
        from osd2f.cli import parse_and_run
        import osd2f.utils

        import copy
        import sys

        assert osd2f.utils.DISK_CONTENT_CONFIG_PATH.find(
            "default_content_settings.yaml"
        )

        cv = osd2f.utils.DISK_CONTENT_CONFIG_PATH

        test_file_path = "./content_config_file_test.yaml"

        sargv = copy.copy(sys.argv)

        sys.argv = ["", "--dry-run", "--generate-current-config", test_file_path]
        parse_and_run()

        sys.argv = [__file__, "--dry-run", "-cc", test_file_path]
        parse_and_run()

        assert osd2f.utils.DISK_CONTENT_CONFIG_PATH == test_file_path

        sys.argv = sargv
        osd2f.utils.DISK_CONTENT_CONFIG_PATH = cv
        os.remove(test_file_path)
