from importlib import reload
from unittest.mock import Mock, patch

from aiounittest.case import AsyncTestCase


class SecretResolverTest(AsyncTestCase):
    def test_load_with_config(self):
        m = Mock()

        with patch("osd2f.security.translate_environment_vars", m):
            import osd2f.config  # imported for side-effect

            # reloaded in case the module was already in cache
            # due to another test
            reload(osd2f.config)

            m.assert_called()  # might be called more than once, depending on cache

    def test_azure_keyvault_env_translation(self):
        def m(s):
            return "resolved" + s

        import os
        from osd2f.security.secrets import azure_keyvault

        os.environ["azure_secret"] = f"{azure_keyvault.PREFIX}::test-keyvault::value"

        other_secret = "another-secret::somehwere::key"
        os.environ["not_azure_secret"] = other_secret

        with patch("osd2f.security.RESOLVERS", {azure_keyvault.PREFIX: m}):
            from osd2f.security import translate_environment_vars

            translate_environment_vars()

            # azure key should be resolved
            assert os.environ["azure_secret"].startswith("resolved")
            # non azure key should not be resolved
            assert os.environ["not_azure_secret"] == other_secret

    def test_azure_keyvault_var_translation(self):
        def m(s):
            return "resolved" + s

        from osd2f.security.secrets import azure_keyvault

        secret = f"{azure_keyvault.PREFIX}::test-keyvault::value"
        other_secret = "another-secret::somehwere::key"

        with patch("osd2f.security.RESOLVERS", {azure_keyvault.PREFIX: m}):
            from osd2f.security import translate_value

            resolved_secret = translate_value(secret)
            unresolved_secret = translate_value(other_secret)

            # azure key should be resolved
            assert resolved_secret.startswith("resolved")
            # non azure key should not be resolved
            assert unresolved_secret == other_secret
