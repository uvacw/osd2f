from osd2f import anonymizers
from aiounittest import AsyncTestCase


class test_anonymizer_package_interface(AsyncTestCase):
    async def test_apply(self):
        from osd2f import anonymizers

        # register a mock pass-through function as an anonymizer
        anonymizers.options["testfunc"] = lambda e, _: e

        entries = [{"title": f"entry {i}"} for i in range(100)]

        redacted_entries = await anonymizers.apply(entries, "testfunc")

        self.assertListEqual(entries, redacted_entries)

        anonymizers.options.pop("testfunc")

    async def test_options_conform_to_spec(self):
        from osd2f import anonymizers

        for k, v in anonymizers.options.items():
            self.assertEqual(k, v.__name__)