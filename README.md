# Prometheus Botnet


## Introduction


## Todo
1. Better error handling


2. Documentation


3. _unfuck the code_


4. **Figure out how to securely and effectively host the C&C server**

  Tor Hidden Service? Can be blocked by firewalls.

   Run through twitter? Can't tansfer large amounts of information in a small period of time.
     
   Cloud hosting? Requires money.
     
   All are options...
  
  
3. Modulation of botnet function. i.e.

  > from elevation import bypassuac
  > from tools import keylogger
  > ...


4. More modules.

  These could be packet sniffer, smb relay, pass-the-hash, etc...


## Dependencies
1. virtualbox

  > apt-get install virtualbox


2. virtualbox guest additions

  Just go to the tool bar at the top of the virtualbox windows and install it on the machine


3. pyhook

  download and install from https://sourceforge.net/projects/pyhook/


4. postgresql database

  > apt-get install postgresql


5. psycopg2 

  > pip install psycopg2
  Or otherwise download from https://pypi.python.org/pypi/psycopg2


## Setup
1. configuation

  To change to callback host and port of the bots edit the create.py file.


2. File configuation

  You may need to go into the code and edit the paths to specific files.


## Screenshots & Examples

