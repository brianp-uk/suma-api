#!/usr/bin/env python3

# suma-list-systems.py
# A script to extract some details of managed client systems from a SUSE Manager server using API.
# 
# It can be used interactively, (no options) and will prompt for required
# information, or non-interactively (-n switch) which reads parameters
# from a .env file.
# 
# Credit: This script is based on the code example in the SUSE Manager 4.2 API documentation at:
#         https://documentation.suse.com/suma/4.2/pdf/4.2_pdf_susemanager_api_doc_color_en.pdf, or
#         https://documentation.suse.com/suma/4.2/api/suse-manager/index.html
#
# version 1.2 - 08-Aug-2022. Brian Petch, SUSE. Added check for the availability
#                                               of the SUSE Manager server/API.
#                                               Added check for the .env file.
#
# version 1.1 - 04-Aug-2022. Brian Petch, SUSE. Moved server FQDN and login credentials
#                                               to a .env file, for improved security.
# version 1.0 - 01-Jul-2022. Brian Petch, SUSE. Initial version.

import sys
import ssl
import os
#import os.path
import urllib.request
import requests
from xmlrpc.client import ServerProxy
from dotenv import load_dotenv
load_dotenv()

argc = len(sys.argv)               # Old (C) habits die hard...

HELP_MESSAGE = "Usage: " +  sys.argv[0] + " [OPTION] \n\n\
Connect to the API of a SUSE Manager server and extract a list of managed client systems and other details.\n\n\
Options:\n\
 -n\t non-interactive mode\n\
 -h\t display help (this message)\n\
 --help\t display help (this message)\n\n\
Interactive mode - call the script with no arguments.\n\
  You will be prompted for the FQDN of the SUSE Manager server and login/password.\n\
Non-interactive mode - call the script with the -n switch.\n\
  This requires the FQDN of the SUSE Manager server and login/password to be specified in a .env file.\n\n\
Warnings:\n\
 Interactive mode will display the entered login/password credentials on screen.\n\
 Non-interactive mode involves storing the login/password details in plain text in a .env file.\n\
 This is helpful for short term repeated usage, but it is recommended that the credentials are deleted after use.\n"

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
        print("Unknown switch.\nTry:",sys.argv[0],"--help")
        exit(1)

# At this point, we either have one argument (-n, for non-interactive) or
# no arguments (interactive).

# In interactive mode, prompt for the SUMA server FQDN and the login/password.
if argc == 1:
   MANAGER_FQDN = input("\nEnter the FQDN of the SUSE Manager server: ")
   MANAGER_URL = 'https://' + MANAGER_FQDN
   MANAGER_API = 'https://' + MANAGER_FQDN + '/rpc/api'
   print ("\nEnter the SUSE Manager access credentials:")
   MANAGER_LOGIN = input("Login: ")
   MANAGER_PASSWORD = input("Password: ")

# In non-interactive mode, the SUMA server FQDN and the login/password variables
# are read from the .env file. 
# Strictly, the if statement below is unnecessary, but left in for ease of 
# future development.
if argc == 2 and sys.argv[1] == "-n":           

   # Check the .env file exists. 
   file_exists = os.path.exists('.env')
   if not file_exists :
     print("Error: non-interactive mode: .env file not found")
     exit(1)

   MANAGER_FQDN=os.getenv("MANAGER_FQDN")
   MANAGER_URL = 'https://' + MANAGER_FQDN
   MANAGER_API = 'https://' + MANAGER_FQDN + '/rpc/api'
   MANAGER_PASSWORD=os.getenv("MANAGER_PASSWORD")
   MANAGER_LOGIN=os.getenv("MANAGER_LOGIN")

def check_connectivity(URL):
  try:
      context = ssl._create_unverified_context()
      request_url = urllib.request.urlopen(URL,context=context)
      return True
  except urllib.request.URLError:
      return False

SERVER_ALIVE = check_connectivity(MANAGER_API)

if not SERVER_ALIVE :
    print("Error: cannot reach the server and/or API at ",MANAGER_API)
    exit(1)

# From the example code in the SUSE Manager documentation:
#   You might need to set to set other options depending on your
#   server SSL configuartion and your local SSL configuration

# Modified to handle the self-signed certificate that's on psuma.  MORE DOCS NEEDED on this.
# context = ssl.create_default_context()     # the original code, using full SSL verification.
context = ssl._create_unverified_context()
client = ServerProxy(MANAGER_API, context=context)
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
