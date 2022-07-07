# suma-api
Code to extract information from a SUSE Manager instance via the XML-RPC API.

This repo originated from a SUSE Hackweek 2022 project 

suma-list-systems.py   is a simple Python script to extract information on client systems managed by a SUSE Manager server.

The script can be run interactively and will prompt for the FQDN of the SUSE Manager server and the login/password.
It can also be run non-interactively via the -n switch.  
At the initial revision this requires the SUSE Manager server FQDN and login/password to be hardcoded with the script.

The script has been tested against the API for SUSE Manager version 4.2 and 4.3.0.

Various improvements would be useful;
  - update to check the server is accessible (network check)
  - update to improve login/password handling in interactive mode (currently displayed on-screen)
  - update to do parameter checking on server FQDN and login/password for non-interactive mode (all null by default)
  
  
  Credits
  Initial efforts leveraged the example code in the SUSE Manager API documentation at:
  https://documentation.suse.com/suma/4.2/api/suse-manager/index.html
  
