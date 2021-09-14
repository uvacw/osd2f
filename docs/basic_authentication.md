# Basic Authentication for easier testing / local installs

## Important note

Basic authentication is not considered a 'safe' authorization mechanism by todays standards. 
This implementation serves to make login testing easier without requiring an OAuth platform
to be available. 

Some reasons why you should not use basic auth in production:
1. Passwords are send unencrypted, so any communication outside HTTPS leaks the password
2. Browsers tend to automatically store basic auth username-password combinations, and do
   so in an insecure fashion

## How does it work

Basic auth will prompt researchers for a username-password combination provided as an environment
configuration. 

```bash

OSD2F_BASIC_AUTH="username21;unguessablepassword" osd2f -m Development
```

Will start a (development) server that allows researchers to login by entering the username `username21` and
password `unguessablepassword`. Needless to say, you must be very carefull about who knows the username and
password.