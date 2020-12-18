"""Fake data factory for Facebook(tm) export data

Data structure was induced from examples provided in 2020.
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
        c = {
            "timestamp": f.unix_time(start_datetime=datetime.datetime(2020, 1, 1)),
            "title": f"{user} replied to {f.name()}'s comment."
            if random.randint(0, 1)
            else f"{user} commented on her own post.",
        }

        if random.randint(0, 4) == 4:
            # attachments appear to be a list of max 1 item
            c["attachments"] = [
                {
                    "data": [
                        {
                            "external_context": {"url": f.url()},
                            "media": {"uri": f.image_url()},  # optional
                        }
                    ]
                }
            ]
        if random.randint(0, 1):
            # data appears to be a list of one item
            c["data"] = [
                {
                    "comment": {
                        # timestamp of comment does not appear to match
                        # that of upper context
                        "timestamp": f.unix_time(
                            start_datetime=datetime.datetime(2020, 1, 1)
                        ),
                        "comment": f.text(),
                        "author": user,
                        "group": f.company(),
                    }
                }
            ]
        return c

    # for some reason, comments are exported with an outer "comments" key
    comments = {"comments": [make_comment() for _ in range(n)]}
    return comments


def generate_posts(user: str, n: int = 10) -> typing.Dict:
    f = faker.Faker()

    def make_post():

        p = {
            "timestamp": f.unix_time(start_datetime=datetime.datetime(2020, 1, 1)),
            "title": f"{user} wrote on {f.name()}'s timeline.",
        }
        # roughly 40% has an attachment
        if random.randint(0, 9) < 4:

            if random.randint(0, 4) == 1:
                p["attachments"] = {
                    # data seems to be a list of one
                    "data": [
                        {
                            "external_context": {
                                "url": f.url(),
                                "name": f.sentence(),  # optional
                                "source": f.company(),  # optional
                            }
                        }
                    ]
                }
            else:
                p["attachments"] = {
                    # data seems to be a list of one
                    "data": [
                        {
                            "external_context": {
                                "url": f.url(),
                            }
                        }
                    ]
                }
        # roughly 40 has a non-empty "data" field
        if random.randint(0, 4) == 1:
            # even when filled, data appears to be a single-item array
            p["data"] = [{"post": f.texts()}]
            # roughly 1% has an "update_timestamp", but to increase coverage
            # we raise the incidence rate here
            if random.randint(0, 9) == 1:
                p["data"][0]["update_timestamp"] = f.unix_time(
                    start_datetime=datetime.datetime.fromtimestamp(p["timestamp"])
                )
        else:
            p["data"] = []

        return p

    posts = [make_post() for _ in range(n)]
    return posts


def generate_likes_and_reactions_pages(user: str, n: int = 10):
    f = faker.Faker()
    # page_likes has the outer key "page_likes"
    page_likes = {
        "page_likes": [
            {
                "name": f.company(),
                "timestamp": f.unix_time(start_datetime=datetime.datetime(2020, 1, 1)),
            }
            for _ in range(n)
        ]
    }
    return page_likes


def generate_likes_and_reactions_posts_and_comments(user: str, n: int = 10):
    f = faker.Faker()
    # likes & reactions have the outer key "reactions"
    reactions = {
        "reactions": [
            {
                "timestamp": f.unix_time(start_datetime=datetime.datetime(2020, 1, 1)),
                # data is an array that is always length 1 in our sample,
                # but I'd be hesitant to assume this in the proverbial "wild"
                "data": [
                    {
                        "reaction": {
                            "reaction": "LIKE" if random.randint(0, 9) != 1 else "LOVE",
                            "actor": user,
                        }
                    }
                ],
                "title": f"{user} likes {f.name()}'s post.",
            }
            for _ in range(n)
        ]
    }
    return reactions


def generate_bundle(
    output_dir: str,
    overwrite: str,
    n_posts: int,
    n_comments: int,
    n_page_reactions: int,
    n_post_or_comments_reactions: int,
    n_post_files: int = 1,
    include_zip_variant=False,
    include_tar_variant=False,
    include_targz_variant=False,
    indents="",
):
    user = faker.Faker().user_name()
    user_dir = f"facebook-{user}-{random.randint(0,3)}"
    if overwrite and output_dir in os.listdir("."):
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
        with open(os.path.join(posts_path, f"your_posts_{i}.json"), "w") as f:
            json.dump(generate_posts(user=user, n=n_posts), f, indent=indents)

    if n_comments:
        comments_path = os.path.join(output_dir, user_dir, "comments")
        os.makedirs(name=comments_path, exist_ok=True)
        with open(os.path.join(comments_path, "comments.json"), "w") as f:
            json.dump(generate_comments(user=user, n=n_comments), f, indent=indents)

    if n_page_reactions:
        page_reactions_path = os.path.join(output_dir, user_dir, "likes_and_reactions")
        os.makedirs(name=page_reactions_path)
        with open(os.path.join(page_reactions_path, "pages.json"), "w") as f:
            json.dump(
                generate_likes_and_reactions_pages(user=user, n=n_page_reactions),
                f,
                indent=indents,
            )

    if n_post_or_comments_reactions:
        post_or_comments_reactions_path = os.path.join(
            output_dir, user_dir, "likes_and_reactions"
        )
        os.makedirs(name=post_or_comments_reactions_path, exist_ok=True)
        with open(
            os.path.join(post_or_comments_reactions_path, "posts_and_comments.json"),
            "w",
        ) as f:
            json.dump(
                generate_likes_and_reactions_posts_and_comments(
                    user=user, n=n_post_or_comments_reactions
                ),
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
        description="Facebook data export mock data generator "
        "this tool generate mock data to test import "
        "functionality of facebook data exports. "
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
        "-pr",
        "--page-reactions",
        type=int,
        help="the number of page reactions to generate",
        default=20,
    )
    parser.add_argument(
        "-pcr",
        "--post-comment-reactions",
        type=int,
        help="the number of posts/comments reactions to generate",
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
        "-z",
        "--include-zip",
        type=bool,
        help="whether to generate a zipped version of the mock data",
        default=True,
    )
    parser.add_argument(
        "-t",
        "--tar",
        type=bool,
        help="whether to generate a '.tar' archive of the mock data",
        default=True,
    )
    parser.add_argument(
        "-tz",
        "--tar-gz",
        type=bool,
        help="whether to generate a '.tar.gz' archive of the mock data",
        default=True,
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
        n_page_reactions=args.page_reactions,
        n_post_or_comments_reactions=args.post_comment_reactions,
        n_post_files=args.n_post_files,
        include_zip_variant=args.include_zip,
        include_tar_variant=args.tar,
        include_targz_variant=args.tar_gz,
        indents=args.indents,
    )
