# Josh Berry
# CodeWatch
# August 2014
# 

import argparse
import xml.etree.ElementTree as ET
import re
import requests
import string
import random
import os
from requests.auth import HTTPBasicAuth
from requests.auth import HTTPDigestAuth

# Get all the arguments for the tool
parser = argparse.ArgumentParser(prog='jnlpdownloader.py', 
	formatter_class=argparse.ArgumentDefaultsHelpFormatter,
	description='Download JAR files associated with a JNLP file',
	epilog='Example: jnlpdownloader.py --link https://www.example.com/java/jnlp/sample.jnlp')
parser.add_argument('--link', 
	required=True,
	help='the full URL to the JNLP file (must include http(s)://')
parser.add_argument('--ntlmuser', 
	default=None,
	help='use NTLM authentication with this username (format of domain \\ username)')
parser.add_argument('--ntlmpass', 
	default=None,
	help='use NTLM authentication with this password')
parser.add_argument('--basicuser', 
	default=None,
	help='use BASIC authentication with this username')
parser.add_argument('--basicpass', 
	default=None,
	help='use BASIC authentication with this password')
parser.add_argument('--digestuser', 
	default=None,
	help='use DIGEST authentication with this username')
parser.add_argument('--digestpass', 
	default=None,
	help='use DIGEST authentication with this password')
parser.add_argument('--cookie', 
	default=None,
	help='use a previously established sessions cookie')

# Stick arguments in a variable and then create a session
args = vars(parser.parse_args())
r = ''
session = requests.Session()

# Random value for directory creation
randDir = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(10))

# Check to see if BASIC/DIGEST/NTLM/Cookie authentication is being performed
# If so, pass credentials to session, if not, just connect to JNLP URL
if args['ntlmuser'] is not None and args['ntlmpass'] is not None:
  from requests_ntlm import HttpNtlmAuth
  session.auth = HttpNtlmAuth(args['ntlmuser'],args['ntlmpass'], session)
  r = session.get(args['link'], verify=False)
elif args['basicuser'] is not None and args['basicpass'] is not None:
  session.auth = HTTPBasicAuth(args['basicuser'],args['basicpass'])
  r = session.get(args['link'], verify=False)
elif args['digestuser'] is not None and args['digestpass'] is not None:
  session.auth = HTTPDigestAuth(args['digestuser'],args['digestpass'])
  r = session.get(args['link'], verify=False)
elif args['cookie'] is not None:
  cookies = {}

  # Check to see if the cookie has a semicolon, if so there might be mutiple cookies
  if re.search(';', args['cookie']):
    cookielist = args['cookie'].split(';')


    # Loop through list of cookies
    for jnlpcookies in cookielist:

      # If there isn't an equal and some sort of content, then it isn't a valid cookie, otherwise add to list of cookies
      if re.search('[a-zA-Z0-9]', jnlpcookies) and re.search('[=]', jnlpcookies):
        cookieparts = jnlpcookies.split('=')
        cookies[cookieparts[0]] = cookieparts[1]

  else:

    # Check to see if cookie has =, if not it is malformed and send dummy cookie
    # If so, split at the = into correct name/value pairs
    if re.search('=', args['cookie']):
      cookielist = args['cookie'].split('=')
      cookies[cookielist[0]] = cookielist[1]
    else:
      cookies['jnlp'] = 'jnlpdownloader'

  r = session.get(args['link'], cookies=cookies, verify=False)
else:
  r = session.get(args['link'], verify=False)

# If the status code is not 200, the file was likely inaccessible so we exit
if r.status_code is not 200:
  print '[*] Link was inaccessible, exiting.'
  exit(0)

xmltree = ''
xmlroot = ''
jnlpurl = ''

# Attempt to read the JNLP XML, if this fails then exit
try:
  xmltree = ET.ElementTree(ET.fromstring(r.content))
except:
  print '[*] JNLP file was misformed, exiting.'
  exit(0)

# Get the XML document structure and pull out the main link
try:
  xmlroot = xmltree.getroot()
  jnlpurl = xmlroot.attrib['codebase']+'/'
except:
  print '[*] JNLP file was misformed, exiting.'
  exit(0)

# If the JNLP file was good, create directory to store JARs
# First get the path delimeter for the OS
path_delim = ''
if 'posix' in os.name:
  path_delim = '/'
else:
  path_delim = '\\'

# Next, try to create the directory or default to current
try:
  if not os.path.exists(os.getcwd() + path_delim + randDir):
    os.mkdir(os.getcwd() + path_delim + randDir)
  else:
    print '[*] Random directory already exists, defaulting to current.'
    randDir = '.'
except:
  print '[*] Failed to create random directory, defaulting to current.'
  randDir = '.'

jnlplinks = []
i = 0

# Loop through each JAR listed in the JNLP file
for jars in xmlroot.iter('jar'):

  # Get the file, path, and URI
  jnlpfile = jars.get('href').rsplit('/')[1]
  jnlppath = jars.get('href').rsplit('/')[0] + '/'
  jnlpuri = jars.get('href')

  # If the JAR has version info, then store it as we might need to use it
  if jars.get('version') is None:
    jnlpalt = None
    jnlpver = None
    altfile = None
  else:
    jnlpalt = jnlppath + jnlpfile.rsplit('.jar')[0] + '__V' + jars.get('version') + '.jar'
    altfile = jnlpfile.rsplit('.jar')[0] + '__V' + jars.get('version') + '.jar'
    jnlpver = jnlpuri + '?version-id=' + jars.get('version') 

  # Add each JAR URI, Version, Filename, Alternate URI, and alternate filename to a list
  # These alternates are based on behavior I have seen where Java uses the version
  # information in the file name
  jnlplinks.append([jnlpuri, jnlpver, jnlpfile, jnlpalt, altfile])
  i+=1

# Loop through each Native Library listed in the JNLP file
for nativelibs in xmlroot.iter('nativelib'):

  # Get the file, path, and URI
  jnlpfile = nativelibs.get('href').rsplit('/')[1]
  jnlppath = nativelibs.get('href').rsplit('/')[0] + '/'
  jnlpuri = nativelibs.get('href')

  # If the Native Library has version info, then store it as we might need to use it
  if nativelibs.get('version') is None:
    jnlpalt = None
    jnlpver = None
    altfile = None
  else:
    jnlpalt = jnlppath + jnlpfile.rsplit('.jar')[0] + '__V' + nativelibs.get('version') + '.jar'
    altfile = jnlpfile.rsplit('.jar')[0] + '__V' + nativelibs.get('version') + '.jar'
    jnlpver = jnlpuri + '?version-id=' + nativelibs.get('version') 

  # Add each JAR URI, Version, Filename, Alternate URI, and alternate filename to a list
  # These alternates are based on behavior I have seen where Java uses the version
  # information in the file name
  jnlplinks.append([jnlpuri, jnlpver, jnlpfile, jnlpalt, altfile])
  i+=1

# Loop through the list of lists with all the URI, version, etc info
for link in jnlplinks:

  # Make a request for the file
  print '[+] Attempting to download: '+jnlpurl+link[0]
  jnlpresp = session.get(jnlpurl + link[0])

  # If the request succeeded, then write the JAR to disk
  if jnlpresp.status_code == 200:
    print '[-] Saving file: '+link[2]+' to '+randDir
    output = open(randDir+'/'+link[2], 'wb')
    output.write(jnlpresp.content)
    output.close()
  else:

    # If the straight request didn't succeed, try to download with version info
    if link[1] is not None:

      # Make a request for the file
      print '[+] Attempting to download: '+jnlpurl+link[1]
      jnlpresp = session.get(jnlpurl + link[1])

      # If the request succeeded, then write the JAR to disk
      if jnlpresp.status_code == 200:
        print '[-] Saving file: '+link[2]+' to '+randDir
        output = open(randDir+'/'+link[2], 'wb')
        output.write(jnlpresp.content)
        output.close()

    # If the straight request didn't succeed, try to download with alternate name
    if link[3] is not None and link[4] is not None:

      # Make a request for the file
      print '[+] Attempting to download: '+jnlpurl+link[3]
      jnlpresp = session.get(jnlpurl + link[3])

      # If the request succeeded, then write the JAR to disk
      if jnlpresp.status_code == 200:
        print '[-] Saving file: '+link[4]+' to '+randDir
        output = open(randDir+'/'+link[4], 'wb')
        output.write(jnlpresp.content)
        output.close()