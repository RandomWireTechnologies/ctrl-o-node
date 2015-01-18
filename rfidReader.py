#!/usr/bin/python

import subprocess # for calling beep for piezo
import RPi.GPIO as GPIO
import time # for sleep
import glob
import os
import logging
import config

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('/var/log/nfc.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('(%(levelname)s) %(asctime)s %(message)s','%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)


RED_LED = 22
BLUE_LED = 17
GREEN_LED = 27
DOOR_LATCH = 2
FILE_CMD_PATH = "/opt/nfc/doorcmds/"
FILE_CMD_GLOB = "/opt/nfc/doorcmds/*"
FILE_CMD_OPEN = "/opt/nfc/doorcmds/open"
FILE_CMD_INIT = "/opt/nfc/doorcmds/init"


def log(data):
        print time.strftime("%Y-%b-%d:%H:%M:%S"),":",data

import nfc
import database

localDB = None
remoteDB = None

def init_gpio():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GREEN_LED, GPIO.OUT) # green LED
    GPIO.setup(BLUE_LED, GPIO.OUT) # blue LED
    GPIO.setup(RED_LED, GPIO.OUT) # red LED
    GPIO.setup(DOOR_LATCH, GPIO.OUT) # relay
    GPIO.output(GREEN_LED, False) # green LED
    GPIO.output(BLUE_LED, False) # blue LED
    GPIO.output(RED_LED, False) # red LED
    if (nodeType == "INTERNAL_DOOR"):
        GPIO.output(DOOR_LATCH, True) # relay 
    else:
        GPIO.output(DOOR_LATCH, False) # relay 

def init():
    global localDB
    global remoteDB
    global nodeType
    localDB = database.MemberDatabase(config.localDBHost,config.localDBUser,config.localDBPass,config.localDBDatabase)
    remoteDB = database.MemberDatabase(config.remoteDBHost,config.remoteDBUser,config.remoteDBPass,config.remoteDBDatabase,config.remoteDBPort,config.remoteDBSSL)
    nodeType = localDB.get_node_type()
    init_gpio()
    clearFileCmds()
    subprocess.call(["/usr/local/bin/beep"])
    nfc.init()



def ledUpdate(mode):
    if (mode == "bad hash"):
        GPIO.output(RED_LED, True)
        GPIO.output(GREEN_LED, True)
    	time.sleep(0.1)
    	GPIO.output(RED_LED, False)
        GPIO.output(GREEN_LED, False)
    	time.sleep(0.1)
    	GPIO.output(RED_LED, True)
        GPIO.output(GREEN_LED, True)
    	time.sleep(0.1)
    	GPIO.output(RED_LED, False)
        GPIO.output(GREEN_LED, False)
    elif (mode == "bad serial"):
        GPIO.output(RED_LED, True)
        time.sleep(0.2)
        GPIO.output(RED_LED, False)
        time.sleep(0.2)
        GPIO.output(RED_LED, True)
        time.sleep(0.2)
        GPIO.output(RED_LED, False)
    elif (mode == "disabled"):
        GPIO.output(RED_LED, True)
        GPIO.output(BLUE_LED, True)
    	time.sleep(0.1)
        GPIO.output(RED_LED, False)
    	GPIO.output(BLUE_LED, False)
    	time.sleep(0.1)
        GPIO.output(RED_LED, True)
    	GPIO.output(BLUE_LED, True)
    	time.sleep(0.1)
        GPIO.output(RED_LED, False)
    	GPIO.output(BLUE_LED, False)
    else:
        GPIO.output(RED_LED, True)
    	time.sleep(0.4)
    	GPIO.output(RED_LED, False)
    	time.sleep(0.4)
    	GPIO.output(RED_LED, True)
    	time.sleep(0.4)
    	GPIO.output(RED_LED, False)



def open_door(unlocked):
    GPIO.output(DOOR_LATCH, True) # relay 
    logger.info("Door unlocked")
    subprocess.call(["/usr/local/bin/beep"])
    # Turn on success LED
    GPIO.output(GREEN_LED, True)
    time.sleep(5)
    # relock door after 5 seconds
    if not unlocked:
        GPIO.output(DOOR_LATCH, False) # relay 
        logger.info("Door locked")
    # Turn off success LED
    GPIO.output(GREEN_LED, False)   
 
def init_card():
    GPIO.output(BLUE_LED, True)
    GPIO.output(RED_LED, True)
    logger.info("Waiting for card to initialze")
    card = nfc.initCard()
    if (card == None):
        # Turn off blue, to leave red on showing error
        GPIO.output(BLUE_LED, False)
        GPIO.output(GREEN_LED, False)
        GPIO.output(RED_LED, True)
        time.sleep(2)
        GPIO.output(RED_LED, False)
        return False
    if remoteDB.check():
        # Check to see if card exists
        cardData = localDB.get_card_data(card[0])
        if cardData != None:
            remoteDB.update_hash(cardData[0],card[1])
            GPIO.output(RED_LED, False)
            GPIO.output(BLUE_LED, False)
            return True
        # Add card to database
        logger.info("Adding new card to database")
        remoteDB.add_card(card[0],card[1])
    GPIO.output(RED_LED, False)
    GPIO.output(BLUE_LED, False)
    return False    
    
def clearFileCmds():
    cmds = glob.glob(FILE_CMD_GLOB)
    for cmd in cmds:
        os.remove(cmd)

def getAutoUnlockedState(db):
    db.check_auto_open()

def checkFileCmd():
    # Check to see if a local file is commanding action and if so do It
    cmds = glob.glob(FILE_CMD_GLOB)
    # Split off the filename from the full path if anything is returned
    if cmds:
        user_id = None
        try:
            fh = open(cmds[0],'r')
            user_id = fh.readline()
            fh.close()
        except:
            logger.info("Failed to read user id from command file")
            user_id = None
        # Check name for a valid command, and execute
        if (cmds[0] == FILE_CMD_OPEN):
            remoteDB.log(None,user_id,"Remote Door Unlock","REMOTE_CMD")
            logger.info("Remote unlock from user "+user_id)
            open_door()
            os.remove(cmds[0])
        elif (cmds[0] == FILE_CMD_INIT):
            remoteDB.log(None,user_id,"Remote Card Init","REMOTE_CMD")
            init_card()    
            os.remove(cmds[0])
            time.sleep(1)
    
    return

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
        

def poll():
    card = None
    unlocked = False
    lastTime = time.time()
    logger.info("Waiting for new card")
    while (card == None):
        card = nfc.getCard()
        checkFileCmd()
        if (time.time()-lastTime > 30):
            new_unlocked = getAutoUnlockedState(localDB)
            if (new_unlocked != unlocked):
                if (unlocked):
                    # Unlock the Door
                    GPIO.output(DOOR_LATCH, True) # relay 
                    logger.info("Door unlocked")
                else:
                    # Lock the Door
                    GPIO.output(DOOR_LATCH, False) # relay 
                    logger.info("Door locked")
            unlocked = new_unlocked                     
        localDB.periodic_database_ping()
        remoteDB.periodic_database_ping()
    logger.info("Card found: serial="+card[0]+" hash="+card[1])
    if not localDB.check():
        logger.info("Local database not connected!")
        return None    
    card_id = localDB.get_valid_card(card[0],card[1],remoteDB)
    if (is_number(card_id) == False):
        ledUpdate("bad serial")
        return None
    # Update card hash if configured
    if (config.rehash):
        new_hash = nfc.generateNewHash(card[1])
        if (nfc.writeHash(new_hash[0])):
            # Update database
            remoteDB.update_hash(card_id,new_hash[1])
        else:
            # Set fault bit on card
            remoteDB.update_hash(card_id,card[1],1)
            ledUpdate("bad hash")
            return None
        
    # Check for access
    access_status = localDB.check_valid_access(card_id, remoteDB)
    if (access_status != True):
        ledUpdate(access_status)
        return None
    else:
        # Log Success
        #db_log(cardData[0],cardData[1],"Access Granted")
        #log("Access Granted: Card ID=%s User ID=%s" % (card_id,cardData[1]))
        # Open Door
        open_door(unlocked)
        return True

# Main
init()
while(1):
    if not poll():
        time.sleep(1)
print "Exited while(1)? We must be done?"
nfc.close()
