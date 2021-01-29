from aiounittest import AsyncTestCase


class test_anonymizer_package_interface(AsyncTestCase):
    async def test_apply(self):
        from osd2f import anonymizers

        # register a mock pass-through function as an anonymizer
        async def testfunc(e, _):
            return e

        anonymizers.options["testfunc"] = testfunc

        entries = [{"title": f"entry {i}"} for i in range(100)]

        redacted_entries = await anonymizers.apply(entries, "testfunc")

        self.assertListEqual(entries, redacted_entries)

        anonymizers.options.pop("testfunc")

    async def test_options_conform_to_spec(self):
        from osd2f import anonymizers

        for k, v in anonymizers.options.items():
            self.assertEqual(k, v.__name__)

    async def test_submission_list_anonymization(self):
        from osd2f import anonymizers
        from osd2f.definitions import Settings, SubmissionList, Submission

        async def testfunc(e, a):
            e[a] = a
            return e

        anonymizers.options["testfunc"] = testfunc

        settings = Settings(
            files={
                "file(_\\d)?.json": {
                    "accepted_fields": [],
                    "anonymizers": [{"testfunc": "a"}, {"testfunc": "b"}],
                }
            }
        )
        submission_list = SubmissionList(
            __root__=[Submission(entries=[{}], filename="file_2.json", submission_id=1)]
        )
        await anonymizers.anonymize_submission_list(
            submission_list=submission_list, settings=settings
        )
        self.assertEqual(submission_list.__root__[0].entries[0], {"a": "a", "b": "b"})
