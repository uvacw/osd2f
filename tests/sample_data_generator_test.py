import glob
import os
import pathlib
import re
import shutil
from unittest import TestCase


class MinimalSampleGeneratorTest(TestCase):
    """Very high-level test of the sample data generator script.

    The Sample script is basically a set of assumptions written as code. As
    such, a full set of tests is not really worthwhile (basically, they would just
    be a repetition of the assumptions).

    Instead, we check whether
        1. the script is importable and runnable
        2. the expected files are generated
        3. generated structure matches that of mock data


    """

    def test_sample_generator_import(self):
        from scripts import sample_data_generator  # noqa

    def test_sample_generator_output(self):
        from scripts.sample_data_generator import generate_bundle

        testdir = "temp_test_data"
        self.assertFalse(pathlib.posixpath.exists(testdir))
        generate_bundle(
            testdir,
            overwrite=False,
            include_tar_variant=True,
            include_targz_variant=True,
            include_zip_variant=True,
            indents=2,
            n_companies_followed=10,
            n_engagement=10,
            n_comments=10,
            n_ads_clicked=10,
            n_post_files=2,
            n_profile_interests=10,
            n_posts=10,
            n_short_messages=10,
        )

        self.assertTrue(glob.glob("temp_test_data/README.md"))
        self.assertTrue(glob.glob("temp_test_data/sample-*.zip"))
        self.assertTrue(glob.glob("temp_test_data/sample-*.tar.gz"))
        self.assertTrue(glob.glob("temp_test_data/sample-*.tar"))
        self.assertTrue(glob.glob("temp_test_data/sample-*/posts/posts_0.json"))
        self.assertTrue(glob.glob("temp_test_data/sample-*/posts/posts_1.json"))
        self.assertTrue(glob.glob("temp_test_data/sample-*/engagement/engagement.json"))
        self.assertTrue(
            glob.glob("temp_test_data/sample-*/short_messages/messages.json")
        )
        self.assertTrue(
            glob.glob(
                "temp_test_data/sample-*/profile_interests/profile_interests.json"
            )
        )
        self.assertTrue(glob.glob("temp_test_data/sample-*/comments/comments.json"))
        self.assertTrue(
            glob.glob("temp_test_data/sample-*/ads_clicked/ads_clicked.json")
        )
        self.assertTrue(
            glob.glob(
                "temp_test_data/sample-*/companies_followed/companies_followed.json"
            )
        )

        shutil.rmtree(testdir)

    def test_sample_mockdata_format_equal_to_script_output(self):
        from scripts.sample_data_generator import generate_bundle

        base_testdir = "temp_test_data"
        testdir = os.path.join(base_testdir, "sample")
        self.assertFalse(pathlib.posixpath.exists(testdir))
        generate_bundle(
            testdir,
            overwrite=False,
            include_tar_variant=True,
            include_targz_variant=True,
            include_zip_variant=True,
            indents=2,
            n_companies_followed=20,
            n_engagement=20,
            n_comments=10,
            n_ads_clicked=10,
            n_post_files=2,
            n_profile_interests=10,
            n_posts=10,
            n_short_messages=10,
        )

        sample_mockdata_paths = glob.glob("mockdata/sample/**", recursive=True)
        testdir_paths = glob.glob(os.path.join(testdir, "**"), recursive=True)

        gp = re.compile("(sample-[A-z-0-9]*)")

        def generalized(ps):
            return [gp.sub("sample-*/", p).split("/", 1)[1] for p in ps]

        self.assertListEqual(
            sorted(generalized(sample_mockdata_paths)),
            sorted(generalized(testdir_paths)),
        )

        shutil.rmtree(base_testdir)
