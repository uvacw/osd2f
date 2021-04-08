# Microsoft Authentication using MSAL

## How does it work? 

The application is registered in the `App registrations` with access rights to *read* user
information (e.g. email). 

Using environment variables, the application is configured to accept only a specific set of
email addresses. 

Users trying to access `/researcher*` paths are redirected to Azure and asked to provide the
application with read access to their information. 

The app uses the access information to check whether the user has an email in the authorized emails list. If so, it sets a session-cookie providing access to the `/researcher` page and downloads.

## Configuring the app in Azure

1. Go to `App registrations`
2. select `New registration`
3. Pick a Name
4. set `accounts in this organizational directory only (Single tenant)`
5. The `Redirect URI` should match the endpoint that requires authentication. 
   For local testing, this could be `http://localhost:5000/researcher`. 


## Configuring the server

The server is configured by passing a serialized JSON object as the `MSAL_CONFIG` environment variable. The contents are something like this: 

```json
{
    "client_id":"a-provided-client-id",  // Application (client) ID
    "secret":"the-application-secret",   // a secret created when generating the app registration
    "tenant_id":"azure-tenant-id",       // Directory (tenant) ID
    // users you want to provide access, note that they
    // should be part of the active directory in the same tenant as 
    // the application
    "allowed_users":"allowed-user-one@azure.nl;allowed_user_two@somewhere.com"
}
```

An example of running this locally would be: 

```bash
export MSAL_CONFIG='{"client_id":"a-provided-client-id",  "secret":"the-application-secret", "tenant_id":"azure-tenant-id", "allowed_users":"allowed-user-one@azure.nl;allowed_user_two@somewhere.com"}'
export OSD2F_SECRET="a-safe-production-secret"

osd2f -m Development -db "sqlite://:memory:" -vv

```