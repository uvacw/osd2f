# Protecting downloads with passwords

To 'nudge' researchers to be carefull with respondent data, it is possible
to set a data-password. This will change researcher downloads from `.json` 
or `.csv` files to zipped versions of these files protected with the
specified password. 

Things to note:

1. The zipfiles use AES encryption, which is stronger, but not supported by default on 
many operating systems. Use OS specific software that suppports this encryption, for example:
  * Linux: [PeaZip](https://peazip.github.io/)
  * Max OSX [The Unarchiver](https://theunarchiver.com/)
  * Windows: [7zip](https://www.7-zip.org/)

2. Long passwords help create better protected files, but never consider password protected
zipfiles to be 'unbreakable'. They protect only to layman users, not motivated attackers.

3. You can use a secret-manager to avoid putting the password direcly into CLI arguments or 
environment variables.

## How to enable password protected downloads:

1. Using environment variables:
```bash
# enable access to the researcher interface by 
# setting basic authentication
export OSD2F_BASIC_AUTH="admin;testpassword" 

# set the password
export OSD2F_DATA_PASSWORD=<your password>

# start the server
osd2f -m Development -vvv
```

2. Using a CLI command
```bash
# enable access to the researcher interface by 
# setting basic authentication
export OSD2F_BASIC_AUTH="admin;testpassword" 

osd2f --download-password <your-password> -m Development
```