# Deploying OSD2F to azure

Make sure you azure CLI client is logged in
```bash
az login
```

## setting up config

Setup desired settings:

```bash
az webapp config appsettings set --name  "osd2f-demo"\
    --settings \
        OSD2F_SECRET=$RANDOM$RANDOM$RANDOM$RANDOM \
        OSD2F_DB_URL="sqlite://:memory:"  \
        OSD2F_MODE="Production"
```
Please note: 

 - **OSD2F_SECRET** : This will introduce a random secret that is different every time
this command is run. The secret is used by the server to maintain
sessions, so running this command will 'logout' any ongoing session.
- **OSD2F_DB_URL** : The database to use, the example has an in-memory database, you will want to change this to the connection string for your project.
- **OSD2F_MODE** : the mode in which to run the server, should pretty much always be production for internet facing deployments. 

**NOTE**: deploying secrets in this way is not 'safe', anyone with 
          admin access to this resource group will be able to see
          the secret!


set the custom startup command. We use the hypercorn ASGI server middleware for performance reasons. 

```bash
az webapp config set \
    --startup-file "python -m hypercorn osd2f.__main__:app -b 0.0.0.0"
```

## deploying the app 

Deploying the app uploads the source code and provisions the application. If you want changes to the code to go live, this is the command to run. 

```bash
az webapp up  \
    --runtime 'python|3.8' \
    --resource-group ICTS-automation-RG \
    --location "West Europe" \
    --name osd2f-demo
```