import glob
import os
import pathlib
import re
import shutil
from unittest import TestCase


class MinimalFacebookGeneratorTest(TestCase):
    """Very high-level test of the facebook data generator script.

    The Facebook script is basically a set of assumptions written as code. As
    such, a full set of tests is not really worthwhile (basically, they would just
    be a repetition of the assumptions).

    Instead, we check whether
        1. the script is importable and runnable
        2. the expected files are generated
        3. generated structure matches that of mock data


    """

    def test_facebook_generator_import(self):
        from scripts import facebook_data_generator  # noqa

    def test_facebook_generator_output(self):
        from scripts.facebook_data_generator import generate_bundle

        testdir = "temp_test_data"
        self.assertFalse(pathlib.posixpath.exists(testdir))
        generate_bundle(
            testdir,
            overwrite=False,
            include_tar_variant=True,
            include_targz_variant=True,
            include_zip_variant=True,
            indents=2,
            n_advertiser_interactions=10,
            n_advertiser_uploads=10,
            n_comments=10,
            n_page_reactions=10,
            n_post_files=2,
            n_post_or_comments_reactions=10,
            n_posts=10,
        )

        self.assertTrue(glob.glob("temp_test_data/README.md"))
        self.assertTrue(glob.glob("temp_test_data/facebook-*.zip"))
        self.assertTrue(glob.glob("temp_test_data/facebook-*.tar.gz"))
        self.assertTrue(glob.glob("temp_test_data/facebook-*.tar"))
        self.assertTrue(glob.glob("temp_test_data/facebook-*/posts/your_posts_0.json"))
        self.assertTrue(glob.glob("temp_test_data/facebook-*/posts/your_posts_1.json"))
        self.assertTrue(
            glob.glob(
                "temp_test_data/facebook-*/likes_and_reactions/posts_and_comments.json"
            )
        )
        self.assertTrue(
            glob.glob(
                "temp_test_data/facebook-*/likes_and_reactions/pages_you've_liked.json"
            )
        )
        self.assertTrue(glob.glob("temp_test_data/facebook-*/comments/comments.json"))
        self.assertTrue(
            glob.glob(
                "temp_test_data/facebook-*/ads_and_businesses/advertisers_you've"
                "_interacted_with.json"
            )
        )
        self.assertTrue(
            glob.glob(
                "temp_test_data/facebook-*/ads_and_businesses/advertisers_who_uploaded"
                "_a_contact_list_with_your_information.json"
            )
        )

        shutil.rmtree(testdir)

    def test_facebook_mockdata_format_equal_to_script_output(self):
        from scripts.facebook_data_generator import generate_bundle

        base_testdir = "temp_test_data"
        testdir = os.path.join(base_testdir, "facebook")
        self.assertFalse(pathlib.posixpath.exists(testdir))
        generate_bundle(
            testdir,
            overwrite=False,
            include_tar_variant=True,
            include_targz_variant=True,
            include_zip_variant=True,
            indents=2,
            n_advertiser_interactions=10,
            n_advertiser_uploads=10,
            n_comments=10,
            n_page_reactions=10,
            n_post_files=2,
            n_post_or_comments_reactions=10,
            n_posts=10,
        )

        facebook_mockdata_paths = glob.glob("mockdata/facebook/**", recursive=True)
        testdir_paths = glob.glob(os.path.join(testdir, "**"), recursive=True)

        gp = re.compile("(facebook-[A-z-0-9]*)")

        def generalized(ps):
            return [gp.sub("facebook-*/", p).split("/", 1)[1] for p in ps]

        self.assertListEqual(
            sorted(generalized(facebook_mockdata_paths)),
            sorted(generalized(testdir_paths)),
        )

        shutil.rmtree(base_testdir)
