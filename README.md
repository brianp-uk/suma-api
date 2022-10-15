# suma-api
Code to extract information from a SUSE Manager instance via the XML-RPC API.

This repo originated from a SUSE Hackweek 2022 project 

suma-list-systems.py   is a simple Python script to extract information on client systems managed by a SUSE Manager server.

The script can be run interactively and will prompt for the FQDN of the SUSE Manager server and the login/password.
It can also be run non-interactively via the -n switch, requiring the details to be provided in a
.env file (see example).

The script has been tested against the API for SUSE Manager version 4.2 and 4.3.0.

Credits
Initial efforts leveraged the example code in the SUSE Manager API documentation at:
https://documentation.suse.com/suma/4.2/api/suse-manager/index.html
  
