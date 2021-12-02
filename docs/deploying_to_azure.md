# Deploying OSD2F to azure

## disclaimer

This documentation is intended to demonstrate how to set up OSD2F as an Azure webapp service. It is oriented towards putting an interface out there to see, but is not set up for actual data collection. The needs and conditions of your specific project may impact the way the app should be configured. Consult you cloud engineer before applying the below steps to understand how to adapt them to your project.

# general preparations

## Make sure you azure CLI client is logged in and selected the appropriate subscription. 

```bash
az login
az account set --subscription <subscription-to-publish-to>
export AZURE_RESOURCE_GROUP=<your-resource-group>
export WEBAPPNAME="osd2f-test" # must be globally unique, e.g. unused on Azure
```

Doublecheck with:
```bash
az account show
```

## creating the webapp

Using webapp up will setup the webapp, the appservice and the plan required. The app won't work before we also apply the other commands. Make sure to be inside the OSD2F folder (locally) when running this command.

```bash
# python 3.9 is in early access on Azure (2021-11-05),
# you can select it in the Settings > Configuration 
# panel of the App Service under `Minor version`
az webapp up  \
    --runtime 'python|3.8' \
    --location "West Europe" \
    --sku F1 \
    --verbose \
    --name $WEBAPPNAME
```

Minor addition for security:
```bash
az webapp identity assign --resource-group $AZURE_RESOURCE_GROUP --name $WEBAPPNAME 
```

# setting up config with in-memory db

## 1. Setup desired settings:

```bash
az webapp config appsettings set --name  $WEBAPPNAME\
    --resource-group $AZURE_RESOURCE_GROUP \
    --settings \
        OSD2F_SECRET=$RANDOM$RANDOM$RANDOM$RANDOM \
        OSD2F_DB_URL="sqlite://:memory:"  \
        OSD2F_MODE="Production"
```
Please note: 

 - **OSD2F_SECRET** : This will introduce a random secret that is different every time
this command is run. The secret is used by the server to maintain
sessions, so running this command will 'logout' any ongoing session.
- **OSD2F_DB_URL** : The database to use, the example has an in-memory database, see the next section for a setup with a proper database.
- **OSD2F_MODE** : the mode in which to run the server, should pretty much always be production for internet facing deployments. 

**NOTE**: deploying secrets in this way is not 'safe', anyone with 
          admin access to this resource group will be able to see
          the secret!

set the custom startup command. We use the hypercorn ASGI server middleware for performance reasons. 

```bash
az webapp config set \
    --resource-group $AZURE_RESOURCE_GROUP \
    --name $WEBAPPNAME \
    --startup-file "python -m hypercorn osd2f.__main__:app -b 0.0.0.0"
```

# setting up config with real database

## 1. Create the database

We'll assume a Postgres database, but anything supported by Tortoise should work. 
## 2. You can now formulate a connection string

test in locally (dont forget to whitelist your IP address in the database firewall rules):

```bash
# you should have the admin user (db_user) password (db_pass) and database name (db_name)
db_user='postgres'; \
db_pass='YOUR-PASSWORD-HERE'; \
db_name="YOUR-DATABASE-NAME-HERE"; \
osd2f -db "postgres://$db_user@$db_name:$db_pass@$db_name.postgres.database.azure.com:5432/postgres?ssl=True"
```

If you see an error related to "hba_config" it probably means access is incorrectly configured. Check:

- [ ] did you add the the database server name after the username? (e.g. `user@database:password` )
- [ ] if you are trying to connect from a local machine, did you whitelist your IP in the database security configuration?
## 3. Set 'Allow access to Azure services' to 'Yes' 

This will allow the webapp to connect. Do this in the security configuration of the database you want to connect to. 

## 4. Setup desired settings:

```bash
az webapp config appsettings set --name  $WEBAPPNAME\
    --settings \
        OSD2F_SECRET=$RANDOM$RANDOM$RANDOM$RANDOM \
        OSD2F_MODE="Production"
```
Please note: 

 - **OSD2F_SECRET** : This will introduce a random secret that is different every time
this command is run. The secret is used by the server to maintain
sessions, so running this command will 'logout' any ongoing session.
- **OSD2F_MODE** : the mode in which to run the server, should pretty much always be production for internet facing deployments. 

**NOTE**: deploying secrets in this way is not 'safe', anyone with 
          admin access to this resource group will be able to see
          the secret! Consider using a [secret store](./using_secret_stores.md)

set the custom startup command. We use the hypercorn ASGI server middleware for performance reasons. 

## 5. Add the connection string
```bash 
db_user='postgres'; \
db_pass='YOUR-PASSWORD-HERE'; \
db_name="YOUR-DATABASE-NAME-HERE"; \
\
az webapp config connection-string set \
    --name $WEBAPPNAME \
    -t PostgreSQL \
    --settings custom1="postgres://$db_user@$db_name:$db_pass@$db_name.postgres.database.azure.com:5432/postgres?ssl=True"
```
## 6. We map the Azure protected database connection strings to the startup command of OSD2F.

```bash
az webapp config set \
    --resource-group "<YOUR-RESOURCE-GROUP>"
    --name $WEBAPPNAME
    --startup-file 'OSD2F_DB_URL=$POSTGRESQLCONNSTR_custom1 python -m hypercorn osd2f.__main__:app -b 0.0.0.0'
```

## HINT: Check the webapp settings 

In the app-service > settings > configurations tab, you can check whether the correct database URL string was received and, under general settings, whether the correct startup command was registered. 

# deploying the app 

Deploying the app uploads the source code and provisions the application. If you want changes to the code to go live, this is the command to run. 

```bash
az webapp up  \
    --runtime 'python|3.8' \
    --location "West Europe" \
    --name $WEBAPPNAME
```

# updating the app

If at a certain point you need to update the app settings (e.g., change from SQLlite to Postgres), you will also need to include the ```resource-group``` parameter in the Azure commands. You can get the resource-group info from the app overview. 

Afterwards, you can define it as an environment variable:
```export RESOURCEGROUPNAME="includethenamehere"```

And include it along with the commands above, after the webapp name. For example:
```
az webapp config connection-string set \
    --name $WEBAPPNAME --resource-group $RESOURCEGROUPNAME\
    ...
```

# applying new configurations (temporary method)

There is currently no configuration interface for the content of the app. You can update remote (e.g. Azure)
webapp content configurations by locally creating a content-file and running the app with the remote
database connection. 

For example:

```bash
OSD2F_DB_URL="<your database string>" \
OSD2F_SECRET="arbitrary string" \
osd2f \
-m Production \
-cc your_content_settings.yaml
```


