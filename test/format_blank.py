#!/usr/bin/python

import pn532
import hashlib
import binascii

pn532.init()
result = pn532.format_blank()
if (result == 1):
	print "Success!"
else:
	print "Failed:\n",result

pn532.close()
