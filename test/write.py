#!/usr/bin/python

import pn532
import hashlib
import binascii

pn532.init()
#print "Starting Value"
#print pn532.read()
print "Waiting for card..."
card = None
while (card == None or card == 0):
	card = pn532.read()
print "Found Serial #",card[0]
print " hash -> ",binascii.hexlify(card[1])
newhash = hashlib.sha256(card[1]).digest()
print "New hash = ",binascii.hexlify(newhash)
print "Writing card"
#newhash = "12345678901234567890123456789012"
status = pn532.write(newhash)
if (status==0):
    print "Write successful"
else:
    print "Write failed: err no",status    
print "Final Hash Value"
print binascii.hexlify(pn532.read()[1])
pn532.close()
