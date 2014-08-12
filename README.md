jnlpdownloader
==============

jnlpdownloader is a Python script that takes a URL to a JNLP and downloads all the associated JARs and native libraries.  Another Java based tool exists that provides this functionality, but this Python version extends the capabilities to include the ability to authenticate with BASIC, DIGEST, NTLM, or cookie authentication.

Requirements
============

requests<BR>
requests_ntlm

Usage
=====

<pre>
usage: jnlpdownloader.py [-h] --link LINK [--ntlmuser NTLMUSER]
                         [--ntlmpass NTLMPASS] [--basicuser BASICUSER]
                         [--basicpass BASICPASS] [--digestuser DIGESTUSER]
                         [--digestpass DIGESTPASS] [--cookie COOKIE]
</pre>

Download JAR files associated with a JNLP file

optional arguments:

<pre>
  -h, --help                show this help message and exit
  --link LINK               the full URL to the JNLP file (must include http(s):// 
                            (default: None)
  --ntlmuser NTLMUSER       use NTLM authentication with this username (format of domain 
                            \\ username) (default: None)
  --ntlmpass NTLMPASS       use NTLM authentication with this password (default: None)
  --basicuser BASICUSER     use BASIC authentication with this username (default: None)
  --basicpass BASICPASS     use BASIC authentication with this password (default: None)
  --digestuser DIGESTUSER   use DIGEST authentication with this username (default: None)
  --digestpass DIGESTPASS   use DIGEST authentication with this password (default: None)
  --cookie COOKIE           use a previously established sessions cookie (default: None)
</pre>

Example: jnlpdownloader.py --link https://www.example.com/java/jnlp/sample.jnlp
