# Keeping configuration information secret

Parts of the configuration of an OSD2F deployment are sensitive. Knowing`OSD2F_SECRET` means 
you can impersonate other users. The `OSD2F_DB_URL` can include the username & password
for the database. 

Secret information should *never* be part of your repository. Generally, OSD2F accepts 
sensitive information via environment variables, which allows your deployment environment
to implement secret management. However, in some situations it is more convenient to 
leverage a secret store, or 'keyvault' directly from the application. This document
lists supported keystore solutions. 

## General usage

When the OSD2F application is started, it looks through the environment variables
and changes variables with known prefixes. It will substitute the environment
variables with the corresponding keystore values in-memory. 

By using the appropriate prefix-format, any environment variable value can be
retrieved on runtime from a secret store.


## Azure keyvault

OSD2F supports the Azure Keyvault solution provided by microsoft. It relies on contextual
authentication through the default credentials in the environment. Azure keyvault references
should follow the format:

> azure-keyvault::your-keyvault-location::name-of-key

For example, if the keyvault is called `osd2f-test`, it should have a location such as
`https://osd2f-test.vault.azure.net/`. We store a database URL with the key name `OSD2F-DB-URL` (azure doesn't accept underscores in key names) and the value `sqlite://keyvault-test`. To use this key (locally), make sure the right credentials are set (e.g. `az login` to the appropriate subscription). Then start OSD2F:

```bash
# we use the normal env variable, but the value is the azure-keyvault specification
# instead of the 'real' value we want to use. 
export OSD2F_DB_URL='azure-keyvault::https://osd2f-test.vault.azure.net/::OSD2F-DB-URL' 
osd2f -m Development
```

Observe that the application makes the expected `keyvault-test` sqlite database file. 

### Requirements when deploying 

If you are deploying a OSD2F app, most likely to Azure, make sure the webapp has the `secret` `Get` and `Key` `Get` permissions. You can add these via the KeyVault Access policies or by issuing the command: 

```bash
export WEBAPP_ID="your webapp PRINCIPLE ID"
export KEYVAULT_NAME="your keyvault name"

az keyvault set-policy \
    --name $KEYVAULT_NAME \
    --object-id $WEBAPP_ID \
    --secret-permissions get \
    --key-permissions get
```
Note that this gives the webapp permission to *all* secrets in this keyvault. We recommend using
separate keyvaults for separate applications or services.