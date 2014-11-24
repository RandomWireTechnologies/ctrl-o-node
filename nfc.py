#!/usr/bin/python

import pn532
import hashlib
import binascii
import time
import config

def init():
    pn532.init()

def close():
    pn532.close()
try:
    log
except:
    def log(data):
        print time.strftime("%Y-%b-%d:%H:%M:%S"),":",data

def getCard():
    card = None
    card = pn532.read()
    if (card == None or card == 0):
        return None
	log("Found Serial # %s" % (card[0]))
    log(" -> hash = %s" % (binascii.hexlify(card[1])))
    return (card[0],binascii.hexlify(card[1]))
    
def generateNewHash(oldHash):
    newhash = hashlib.sha256("%s %s %s" % (oldHash,config.hashSecret,str(time.time()))).digest()
    return (newhash,binascii.hexlify(newhash))

def writeHash(hash):
    status = pn532.write(hash)
    if (status==0):
        log(" -> Write successful")
    else:
        log(" -> Write failed: err no "+status)
        return False
    card = pn532.read()
    if (card == None or card == 0):
        log(" -> Failed to read after write")
        return False
    if (card[1] != hash):
        log(" -> Failed to verify hash")
        return False
    # If all that didn't fail, we must have succeeded!
    return True

def initCard():
    log("Request to init new card")
    card = None
    while (card == None or card == 0):
    	card = pn532.read()
    if (pn532.format() != 1):
    	log("Failed to format card")
    	return None
    newhash = hashlib.sha256("%s %s %s" % (card[0],config.hashSecret,str(time.time()))).digest()
    status = pn532.write(newhash)
    if (status != 0):
        log("Write failed: %s",(status))
        return None
        retries = 0
        while(True):
            card2 = pn532.read()
            if ((card2[0] == card[0]) & (card2[1]==newhash)):
                break
            retries = retries + 1
            if (retries > 5):
                break    
        if ((card2[0] != card[0]) | (card2[1]!=newhash)):
            log("Verify failed")
            return None
    log ("New card written serial=%s : hash=%s" % (card[0],binascii.hexlify(newhash)))
    return(card[0],binascii.hexlify(newhash))
