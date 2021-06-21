from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from ...logger import logger

PREFIX = "azure-keyvault"


def azure_keyvault_replace(value: str) -> str:
    """translates environment variables formatted like:

    azure-keyvault::example.vault.azure.net::secret_name

    to the contents of the referred secrets.

    """
    if len(value.split("::")) != 3:
        logger.critical(
            f"azure value {value} is incorrectly formatted, "
            f"should be `{PREFIX}::KEYVAULT_URL::SECRET_NAME`"
        )
        exit()
    _, keyvault_url, secret_name = value.split("::")
    cred = DefaultAzureCredential()
    client = SecretClient(keyvault_url, cred)
    secret = client.get_secret(secret_name).value
    return secret
