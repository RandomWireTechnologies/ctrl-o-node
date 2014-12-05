#!/usr/bin/python

import os
import shutil
import hashlib
import subprocess


# Check and copy config files from templates
if not (os.path.isfile("mifare_key.h")):
    print "Enter your card encryption secret:"
    hashvalue = hashlib.sha1(raw_input()).hexdigest()
    shutil.copy("mifare_key_template.h","mifare_key.h")
    newHash = "0x%s, 0x%s, 0x%s, 0x%s, 0x%s, 0x%s" % (hashvalue[0:2],hashvalue[2:4],hashvalue[4:6],hashvalue[6:8],hashvalue[8:10],hashvalue[10:12])
    rc = subprocess.call("sed -i'' -r 's/(^#define\s+MIFARE_KEY\s+\{)[0-9a-fA-Fx, ]+(\}.*)/\1%s\2/' mifare_key.h" % newHash)
    # assuming it worked for now
    

# Generate client key and certificate request