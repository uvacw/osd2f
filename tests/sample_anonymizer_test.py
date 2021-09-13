from aiounittest import AsyncTestCase


class test_redact_text(AsyncTestCase):
    def test_in_options(self):
        from osd2f.anonymizers.sample_platform import redact_text
        from osd2f.anonymizers import options

        self.assertTrue(redact_text.__name__ in options)

    async def test_parses_title(self):
        from osd2f.anonymizers.sample_platform import redact_text

        user = "henk"
        correspondent = "arie"
        title = f"{user} wrote on {correspondent}'s timeline."

        entry = {"title": title}
        redacted = await redact_text(entry)

        self.assertIsNotNone(redacted)
        self.assertFalse(user in redacted["title"])
        self.assertFalse(correspondent in redacted["title"])

    async def test_parses_post(self):
        from osd2f.anonymizers.sample_platform import redact_text

        user = "henk"
        correspondent = "arie"
        title = f"{user} wrote on {correspondent}'s timeline."
        post = f"Hey {correspondent}, how's life? missing you! -{user}"
        entry = {"title": title, "data": [{"post": post}]}

        redacted = await redact_text(entry)

        self.assertIsNotNone(redacted)
        self.assertFalse(user in redacted["data"][0]["post"])
        self.assertFalse(correspondent in redacted["data"][0]["post"])
