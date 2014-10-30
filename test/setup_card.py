#!/usr/bin/python

import pn532
import hashlib
import binascii
import time

pn532.init()

card = None
while (card == None or card == 0):
	card = pn532.read()
if (pn532.format() != 1):
	print "Failed to format"
	exit()
newhash = hashlib.sha256(card[0]+"newSecretValue"+time.time()).digest()
#print "New hash = ",binascii.hexlify(newhash)
#print "Writing card"
#newhash = "12345678901234567890123456789012"
status = pn532.write(newhash)
if (status != 0):
    print "Write failed:\n",status
card2 = pn532.read()
if (card2 == card):
    #Store in database

print "Success"
#print "Starting Value"
#print pn532.read()
#print "Waiting for card..."
#card = None
#while (card == None or card == 0):
#	card = pn532.read()
#print "Found Serial #",card[0]
#print " hash -> ",binascii.hexlify(card[1])
pn532.close()
