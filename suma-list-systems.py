#!/usr/bin/env python3

# suma-list-systems.py
# A script to extract the details of managed client systems from a SUSE Manager server using API.
# 
# Credit: This script is based on the code example in the SUSE Manager 4.2 API documentation at:
#         https://documentation.suse.com/suma/4.2/pdf/4.2_pdf_susemanager_api_doc_color_en.pdf, or
#         https://documentation.suse.com/suma/4.2/api/suse-manager/index.html
#
# version 1.0 - 01-Jul-2022. Brian Petch, SUSE. Initial version.

import sys
import ssl
from xmlrpc.client import ServerProxy

#print("prog name:", sys.argv[0], "\tfirst arg:", sys.argv[1])

argc = len(sys.argv)               # Old (C) habits die hard...

HELP_MESSAGE = "Usage: " +  sys.argv[0] + " [OPTION] \n\n\
Connect to the API of a SUSE Manager server and extract a list of managed client systems and other details.\n\n\
Options:\n\
 -n\t non-interactive mode\n\
 -h\t display help (this message)\n\
 --help\t display help (this message)\n\
Interactive mode - call the script with no arguments.\n\
  You will be prompted for the FQDN of the SUSE Manager server and login/password.\n\
Non-interactive mode - call the script with the -n switch.\n\
  This requires the FQDN of the SUSE Manager server and login/password to be hardcoded into the script first.\n\n\
Warnings:\n\
 Interactive mode will display the entered login/password credentials on screen.\n\
 Non-interactive mode involves leaving the login/password details in plain text inside the script. It is helpful for short term repeated usage, but it is recommended that they are deleted after use.\n"

if argc == 1:
    print("(interactive mode - Warning: credentials will be displayed on screen)")
elif argc > 2:
    print("Too many arguments.")
    exit(1)
else:
    if sys.argv[1] == "-h":
        print(HELP_MESSAGE)
        exit(1)
    elif sys.argv[1] == "--help":
        print(HELP_MESSAGE)
        exit(1)
    elif sys.argv[1] == "-n":
        print("(non-interactive mode)")
    else:
        print("Unknown switch.")
        exit(1)


# To run in non-interactive mode, change the variables below to suit your environment.
# Examples
#MANAGER_URL = "https://manager.example.com/rpc/api"
#MANAGER_LOGIN = "username"
#MANAGER_PASSWORD = "password"
MANAGER_URL = ""
MANAGER_LOGIN = ""
MANAGER_PASSWORD = ""

# In interactive mode, prompt for the SUMA server FQDN and the login/password.
if argc == 1:
   MANAGER_FQDN = input("\nEnter the FQDN of the SUSE Manager server: ")
   MANAGER_URL = 'https://' + MANAGER_FQDN + '/rpc/api'
   print ("\nEnter the SUSE Manager access credentials:")
   MANAGER_LOGIN = input("Login: ")
   MANAGER_PASSWORD = input("Password: ")

# Should really add a test here, to check that the requested server is reachable on the network.

# From the example code;
# You might need to set to set other options depending on your
# server SSL configuartion and your local SSL configuration

# Modified to handle the self-signed certificate that's on psuma.  MORE DOCS NEEDED on this.
# context = ssl.create_default_context()     # the original code, using full SSL verification.
context = ssl._create_unverified_context()
client = ServerProxy(MANAGER_URL, context=context)
key = client.auth.login(MANAGER_LOGIN, MANAGER_PASSWORD)

# Fill an array called system_list using call to the API method listSystems, via the XML-RPC client proxy.
system_list = client.system.list_systems(key)             # list of ALL systems.

system_count = len(system_list)
print ("\nFound ", system_count , "systems being managed by the SUMA Server at:", MANAGER_URL, "\n")

id_list = [row['id'] for row in system_list]      ## This is a 'list comprehension expression'. Extract the id column from the array (list).
#print (id_list)                                  ## Remember, the array is a list of dictionaries, so it is indexed by keys, not position.

# In the block below, we loop over the list of suma-id's, not just an arbitrary index. 
# We only need the counter variable for output prettiness.

# Print the output column headers.
print(" ", "\t SUMA-id", "\t Hostname", "\t\t\t\t\t OS", "\t Version", "Last check-in")
counter=0
for system in id_list:
    hostname = system_list[counter]['name']
    installed_sw_details = client.system.get_installed_products(key,system)      # This method is called per-system.
    os_name = installed_sw_details[0]['name']
    os_version = installed_sw_details[0]['version']
    checkin = system_list[counter]['last_checkin']
    print(counter + 1,"\t",system,"\t",hostname,"\t",os_name,"\t",os_version,"\t",checkin)
    counter = counter + 1

print()

# Make sure we logout of the XML-RPC proxy.
client.auth.logout(key)
