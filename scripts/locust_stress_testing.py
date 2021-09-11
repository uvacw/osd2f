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

from scripts import sample_data_generator


class SampleParticipant(FastHttpUser):
    wait_time = between(0.1, 5)

    def on_start(self):
        """Generate a fake user and associated donation"""
        f = faker.Faker()
        self.user = f.user_name()
        self.sid = f.uuid4()
        self.entries = {
            "comments.json": flatmap(
                sample_data_generator.generate_comments(user=self.user, n=1000),
                "comments",
            ),
            f"your_posts_{self.user}_1.json": flatmap(
                sample_data_generator.generate_posts(self.user, n=100)
            ),
            "engagement.json": flatmap(
                sample_data_generator.generate_engagement(self.user, 10),
                "engagement",
            ),
            "companies_followed.json": flatmap(
                sample_data_generator.generate_companies_followed(self.user, 100),
                "companies_followed",
            ),
            "ads_clicked.json": flatmap(
                sample_data_generator.generate_ads_clicked(self.user, 50),
                "ads_clicked",
            ),
            "profile_interests.json": [
                {"entry": e}
                for e in flatmap(
                    sample_data_generator.generate_profile_interests(  # noqa
                        self.user, 100
                    ),
                    "profile_interests",
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
