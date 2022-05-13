"""Synthethic dataset factory for example export data from a Data Download Package

"""

import argparse
import datetime
import json
import os
import random
import shutil
import tarfile
import typing

import faker


def generate_comments(user: str, n: int = 10) -> typing.Dict:
    f = faker.Faker()

    def make_comment():
        tt = random.randint(0, 5)
        if tt == 1:
            title = f"{user} posted a reply to {f.name()}'s comment."
        elif tt == 2:
            title = f"{user} created a new comment."
        elif tt == 3:
            title = f"{user} posted a comment on the post by {f.name()}."
        elif tt == 4:
            title = f"{user} posted a comment on the video by {f.name()}"
        else:
            title = f"{user} posted a comment on the photo by {f.name()}"

        c = {
            "timestamp": f.unix_time(start_datetime=datetime.datetime(2020, 1, 1)),
            "title": title,
        }

        if random.randint(0, 1):
            c["information"] = [
                {
                    "comment": {
                        "comment_text": f.text(),
                        "username_author": user,
                    }
                }
            ]
        return c

    comments = {"comment_information": [make_comment() for _ in range(n)]}
    return comments


def generate_posts(user: str, n: int = 10) -> typing.List[typing.Dict]:
    f = faker.Faker()

    def make_post():

        p = {
            "timestamp": f.unix_time(start_datetime=datetime.datetime(2020, 1, 1)),
            "post_title": f"{user} wrote a new post.",
            "keywords": [f.name() for _ in range(random.randint(0, 3))],
        }
        if random.randint(0, 9) < 7:
            p["information"] = {
                "post": [
                    {
                        "post_metadata": {
                            "expanded_url": f.url(),
                            "source": f.company(),  # optional
                        },
                        "post_text": f.text(),
                    }
                ]
            }

        else:
            p["information"] = []

        return p

    posts = [make_post() for _ in range(n)]
    return posts


def generate_companies_followed(user: str, n: int = 10):
    f = faker.Faker()
    companies_followed = {
        "companies_followed": [
            {
                "company_name": f.company(),
                "timestamp": f.unix_time(start_datetime=datetime.datetime(2020, 1, 1)),
            }
            for _ in range(n)
        ]
    }
    return companies_followed


def generate_engagement(user: str, n: int = 10):
    f = faker.Faker()
    engagement = {
        "engagement_info": [
            {
                "timestamp": f.unix_time(start_datetime=datetime.datetime(2020, 1, 1)),
                "engagement_type": random.choice(
                    ["like", "share", "recommend", "listen", "click"]
                ),
                "object": "uuid" + str(random.randint(5000, 9000000)),
            }
            for _ in range(n)
        ]
    }
    return engagement


def generate_ads_clicked(user: str, n: int = 10):
    f = faker.Faker()
    ads_clicked = []
    for _ in range(n):
        ads_clicked.append(
            {
                "ad_title": f.catch_phrase(),
                "activity": random.choice(["click", "expand", "watch"]),
                "timestamp": f.unix_time(start_datetime=datetime.datetime(2020, 1, 1)),
            }
        )
    return ads_clicked


def generate_profile_interests(user: str, n: int = 10):
    f = faker.Faker()
    return {"profile_interests": [f.catch_phrase() for _ in range(n)]}


def generate_short_messages(user: str, n: int = 100):
    f = faker.Faker()
    messages = [
        {"id": f"{f.unix_time()}{f.random_number(5)}", "message": f.paragraph(3)}
        for _ in range(n)
    ]

    return {"messages.collection": messages}


def generate_bundle(
    output_dir: str,
    overwrite: str,
    n_posts: int,
    n_comments: int,
    n_companies_followed: int,
    n_engagement: int,
    n_ads_clicked: int,
    n_profile_interests: int,
    n_post_files: int,
    n_short_messages: int,
    include_zip_variant=False,
    include_tar_variant=False,
    include_targz_variant=False,
    indents="",
):
    user = faker.Faker().user_name()
    user_dir = f"sample-platform-{user}-{random.randint(0,3)}"
    if overwrite and os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(name=output_dir)

    with open(os.path.join(output_dir, "README.md"), "w") as readme:
        readme.write(
            """
# THIS FOLDER CONTAINS MOCK-DATA

## Data was generated using [faker](https://faker.readthedocs.io/en/master/)

## Any similarity to real-world data is purely due to chance
        """
        )

    for i in range(n_post_files):
        posts_path = os.path.join(output_dir, user_dir, "posts")
        os.makedirs(name=posts_path, exist_ok=True)
        with open(os.path.join(posts_path, f"posts_{i}.json"), "w") as f:
            json.dump(generate_posts(user=user, n=n_posts), f, indent=indents)

    if n_comments:
        comments_path = os.path.join(output_dir, user_dir, "comments")
        os.makedirs(name=comments_path, exist_ok=True)
        with open(os.path.join(comments_path, "comments.json"), "w") as f:
            json.dump(generate_comments(user=user, n=n_comments), f, indent=indents)

    if n_companies_followed:
        companies_followed_path = os.path.join(
            output_dir, user_dir, "companies_followed"
        )
        os.makedirs(name=companies_followed_path)
        with open(
            os.path.join(companies_followed_path, "companies_followed.json"), "w"
        ) as f:
            json.dump(
                generate_companies_followed(user=user, n=n_companies_followed),
                f,
                indent=indents,
            )

    if n_engagement:
        engagement_path = os.path.join(output_dir, user_dir, "engagement")
        os.makedirs(name=engagement_path, exist_ok=True)
        with open(
            os.path.join(engagement_path, "engagement.json"),
            "w",
        ) as f:
            json.dump(
                generate_engagement(user=user, n=n_engagement),
                f,
                indent=indents,
            )
    if n_ads_clicked:
        ads_clicked_path = os.path.join(
            output_dir,
            user_dir,
            "ads_clicked",
        )
        os.makedirs(name=ads_clicked_path, exist_ok=True)
        with open(
            os.path.join(ads_clicked_path, "ads_clicked.json"),
            "w",
        ) as f:
            json.dump(
                generate_ads_clicked(user=user, n=n_ads_clicked),
                f,
                indent=indents,
            )
    if n_profile_interests:
        profile_interests_path = os.path.join(output_dir, user_dir, "profile_interests")
        os.makedirs(profile_interests_path, exist_ok=True)
        with open(
            os.path.join(
                profile_interests_path,
                "profile_interests.json",
            ),
            "w",
        ) as f:
            json.dump(
                generate_profile_interests(user=user, n=n_profile_interests),
                f,
                indent=indents,
            )

    if n_short_messages:
        short_messages_path = os.path.join(output_dir, user_dir, "short_messages")
        os.makedirs(short_messages_path, exist_ok=True)
        with open(os.path.join(short_messages_path, "messages.json"), "w") as f:
            json.dump(
                generate_short_messages(user=user, n=n_short_messages),
                f,
                indent=indents,
            )

    if include_zip_variant:
        shutil.make_archive(os.path.join(output_dir, f"{user_dir}"), "zip", output_dir)

    if include_tar_variant:
        shutil.make_archive(os.path.join(output_dir, f"{user_dir}"), "tar", output_dir)

    if include_targz_variant:
        with tarfile.open(
            os.path.join(output_dir, f"{user_dir}.tar.gz"), "w:gz"
        ) as tar:
            tar.add(output_dir, arcname=os.path.basename(output_dir))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sample data export mock data generator "
        "this tool generate mock data to test import "
        "functionality of a sample data export from a general platform. "
        "Note that not all types of exports are currently supported.",
    )

    parser.add_argument(
        "-o",
        "--output",
        help="the directory in which to put generated data.",
        required=True,
    )
    parser.add_argument(
        "--overwrite",
        help="whether to overwrite the directory if it already exists. "
        "Removes *all* content before starting",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "-p", "--n-posts", type=int, help="number of posts to generate", default=100
    )
    parser.add_argument(
        "-c",
        "--n-comments",
        type=int,
        help="the number of comments to generate",
        default=50,
    )
    parser.add_argument(
        "-cf",
        "--companies-followed",
        type=int,
        help="the number of companies followed to generate",
        default=20,
    )
    parser.add_argument(
        "-e",
        "--engagement",
        type=int,
        help="the number of engagement activities to generate",
        default=20,
    )
    parser.add_argument(
        "-np",
        "--n-post-files",
        type=int,
        help="the amount of separate files of posts to generate",
        default=2,
    )
    parser.add_argument(
        "-ac",
        "--ads-clicked",
        type=int,
        help="the number of ads clicked to generate",
        default=10,
    )
    parser.add_argument(
        "-pi",
        "--profile-interests",
        type=int,
        help="the number of profile interests",
        default=10,
    )
    parser.add_argument(
        "-sm",
        "--short-messages",
        type=int,
        help="the number of short messages to generate",
        default=50,
    )
    parser.add_argument(
        "-z",
        "--include-zip",
        action="store_true",
        help="whether to generate a zipped version of the mock data",
        default=False,
    )
    parser.add_argument(
        "-t",
        "--tar",
        action="store_true",
        help="whether to generate a '.tar' archive of the mock data",
        default=False,
    )
    parser.add_argument(
        "-tz",
        "--tar-gz",
        action="store_true",
        help="whether to generate a '.tar.gz' archive of the mock data",
        default=False,
    )
    parser.add_argument(
        "-i",
        "--indents",
        type=int,
        help="the integer indentation level",
        default=0,
    )

    args = parser.parse_args()
    generate_bundle(
        output_dir=args.output,
        overwrite=args.overwrite,
        n_posts=args.n_posts,
        n_comments=args.n_comments,
        n_companies_followed=args.companies_followed,
        n_engagement=args.engagement,
        n_ads_clicked=args.ads_clicked,
        n_profile_interests=args.profile_interests,
        n_post_files=args.n_post_files,
        n_short_messages=args.short_messages,
        include_zip_variant=args.include_zip,
        include_tar_variant=args.tar,
        include_targz_variant=args.tar_gz,
        indents=args.indents,
    )
