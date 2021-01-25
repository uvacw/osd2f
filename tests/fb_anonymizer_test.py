from aiounittest import AsyncTestCase


class test_fb_redact_posts_usernames_based_on_title(AsyncTestCase):
    def test_in_options(self):
        from osd2f.anonymizers.facebook import fb_redact_posts_usernames_based_on_title
        from osd2f.anonymizers import options

        self.assertTrue(fb_redact_posts_usernames_based_on_title.__name__ in options)

    async def test_parses_title(self):
        from osd2f.anonymizers.facebook import fb_redact_posts_usernames_based_on_title

        user = "henk"
        correspondent = "arie"
        title = f"{user} wrote on {correspondent}'s timeline."

        entry = {"title": title}
        redacted = await fb_redact_posts_usernames_based_on_title(entry)

        self.assertIsNotNone(redacted)
        self.assertFalse(user in redacted["title"])
        self.assertFalse(correspondent in redacted["title"])

    async def test_parses_post(self):
        from osd2f.anonymizers.facebook import fb_redact_posts_usernames_based_on_title

        user = "henk"
        correspondent = "arie"
        title = f"{user} wrote on {correspondent}'s timeline."
        post = f"Hey {correspondent}, how's life? missing you! -{user}"
        entry = {"title": title, "data": [{"post": post}]}

        redacted = await fb_redact_posts_usernames_based_on_title(entry)

        self.assertIsNotNone(redacted)
        self.assertFalse(user in redacted["data"][0]["post"])
        self.assertFalse(correspondent in redacted["data"][0]["post"])
