"""Locust based stress testing

Run headless using:

locust --host http://localhost:5000 -f scripts/locust_stress_test.py \
    --headless --users 100 -t 60sec

Run with web interface:

locust -f scripts/locust_stress_test.py

NOTE: it's recommended to use a ASGI tool such as hypercorn in production,
      you should also test with such a framework to get realistic performance.

"""
import faker

from locust import between, task
from locust.contrib.fasthttp import FastHttpUser

from osd2f.utils import flatmap

from scripts import facebook_data_generator


class FacebookParticipant(FastHttpUser):
    wait_time = between(0.1, 5)

    def on_start(self):
        """Generate a fake user and associated donation"""
        f = faker.Faker()
        self.user = f.user_name()
        self.sid = f.uuid4()
        self.entries = {
            "comments.json": flatmap(
                facebook_data_generator.generate_comments(user=self.user, n=1000),
                "comments",
            ),
            f"your_posts_{self.user}_1.json": flatmap(
                facebook_data_generator.generate_posts(self.user, n=100)
            ),
            "pages.json": flatmap(
                facebook_data_generator.generate_likes_and_reactions_pages(
                    self.user, 10
                ),
                "page_likes",
            ),
            "posts_and_comments.json": flatmap(
                facebook_data_generator.generate_likes_and_reactions_posts_and_comments(
                    self.user, 100
                ),
                "reactions",
            ),
            "advertisers_you've_interacted_with.json": flatmap(
                facebook_data_generator.generate_advertisers_youve_interacted_with(
                    self.user, 50
                ),
                "history",
            ),
            "advertisers_who_uploaded_a_contact_list_with_your_information.json": [
                {"entry": e}
                for e in flatmap(
                    facebook_data_generator.generate_advertisers_who_uploaded_a_contact_list_with_your_information(  # noqa
                        self.user, 100
                    ),
                    "custom_audiences",
                )
            ],
        }

    @task(20)
    def send_log(self):
        self.client.get("/log?position=locust&level=DEBUG")

    @task(1)
    def send_anonymization(self):
        for fn, entries in self.entries.items():
            self.client.post(
                "/adv_anonymize_file",
                json={
                    "submission_id": self.sid,
                    "filename": fn,
                    "n_deleted": 0,
                    "entries": entries,
                },
            )

    @task(1)
    def send_submission(self):
        submission = []
        for fn, entries in self.entries.items():
            submission.append(
                {
                    "submission_id": self.sid,
                    "filename": fn,
                    "n_deleted": 0,
                    "entries": entries,
                }
            )
        self.client.post("/upload", json=submission)
