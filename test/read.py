#!/usr/bin/python

import pn532
import binascii

pn532.init()
card = pn532.read()
print "Card Serial #",card[0]," Hash=",binascii.hexlify(card[1])
pn532.close()
