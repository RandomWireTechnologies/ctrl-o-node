#!/usr/bin/python

import MySQLdb
import socket # for getting hostname/node_id
import time
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('/var/log/nfc.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('(%(levelname)s) %(asctime)s %(message)s','%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)


def is_number(s):
    try:
        float(s)
        return True
    except:
        return False

# Database class
class MemberDatabase():
    def __init__(self,host="localhost",user="",passwd="",database=None,port=3306,ssl=None):
        # Setup database handlers
        self.sqlCacheFile = "/opt/nfc/cache/%s_log.sql" % (host)
        self.hostname = (socket.gethostname())
        self.host = host
        self.user = user
        self.passwd = passwd
        self.database = database
        self.port = port
        self.ssl = ssl
        self.dbh = None
        self.cur = None
        self.lastPing = time.time()
        self.pingRate = 30 # This is the time in seconds between database pings
        self.connect()
        
    def connect(self):
        # Check for connection then try to connection
        try:
            self.dbh = MySQLdb.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.database, port=self.port, ssl=self.ssl) # name of the data base
            self.cur = self.dbh.cursor()
            logger.info("Connected to database : %s" % self.host)
            return True
        except:
            if (self.cur != None):
                self.cur.close()
            self.cur = None
            self.dbh = None
            logger.info("Failed to connect to database : %s" % self.host)
            return False        
        
    def ping(self):
        # Check database connection
        return self.dbh.ping()
    
    def check(self):
        # Check database status
        self.lastPing = time.time()
        if (self.dbh == None):
            # Try to connect
            success = self.connect()
            if (success):
                self.push_cache_commands()
            return success
        else:
            try:
                self.dbh.ping()
                return True
            except:
                self.cur.close()
                self.cur = None
                self.dbh = None
                return False
    
    def periodic_database_ping(self):
        if ((time.time()-self.lastPing) > self.pingRate):
            self.check()
    
    def get_node_type(self):
        if(self.check() == False):
            return None
        result = self.cur.execute("""SELECT type from nodes where name=%s""",self.hostname)
        self.dbh.commit()
        if (result > 0):
            return self.cur.fetchone()[0]
        return None
    
    def log(self,card_id,user_id,status,type='DOOR_SWYPE'):
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        if(self.check()):
            node_status = self.cur.execute("""SELECT id from nodes where name=%s""",self.hostname)
            if(node_status > 0):
                node_id = self.cur.fetchone()[0]
                if((card_id == None) or (card_id == "")) and ((user_id == None) or (user_id == "")):
                    insert_data = "INSERT INTO log VALUES (NULL,'%s',NULL,NULL,'%s','%s',NULL,NULL,'%s')" % (node_id,now,type,status)
                elif (user_id == None) or (user_id == ""):
                    insert_data = "INSERT INTO log VALUES (NULL,'%s','%s',NULL,'%s','%s',NULL,NULL,'%s')" % (node_id,card_id,now,type,status)
                elif (card_id == None) or (card_id == ""):
                    insert_data = "INSERT INTO log VALUES (NULL,'%s',NULL,'%s','%s','%s',NULL,NULL,'%s')" % (node_id,user_id,now,type,status)
                else:    
                    insert_data = "INSERT INTO log VALUES (NULL,'%s','%s','%s','%s','%s',NULL,NULL,'%s')" % (node_id,card_id,user_id,now,type,status)
                self.cur.execute(insert_data)
                self.dbh.commit()
                return True
            # Save update to sql cache
            self.cache_sql(insert_data)
    
    def get_card_data(self, card_serial):
        # Find card in database
        cards_found = self.cur.execute("""select * from cards where serial=%s""",card_serial)
        self.dbh.commit()
        if (cards_found == 0):
            return None
        card_data = self.cur.fetchone()
        return card_data
    
    def get_valid_card(self, card_serial, card_hash, remote_db):
        # Find card in database
        cards_found = self.cur.execute("""select id,hash,enabled,fault,user_id from cards where serial=%s""",card_serial)
        self.dbh.commit()
        if (cards_found == 0):
            # Card not found
            logger.info("Error finding card serial: "+card_serial)
            remote_db.log(None,None,"Access Denied - Serial "+card_serial+" not found")
            return "No card found"
        card_data = self.cur.fetchone()
        # Check card hash
        if (card_data[1] != card_hash):
            if (card_data[3] == 0):    
                logger.info("Error matching hash: card="+card_serial+",db="+card_data[1])
                remote_db.log(card_data[0],card_data[4],"Access Denied - Bad Hash")
                return "Bad hash"    
        # Check card enabled 
        if (card_data[2] == 0):
            logger.info("Error - Card Id "+str(card_data[0])+" Disabled")
            remote_db.log(card_data[0],card_data[4],"Access Denied - Card Disabled")
            return "Card disabled"
        # Valid card, so return the card_id
        return card_data[0]     
        
    
    def check_valid_access(self,card_id,remote_db):
        users_found = self.cur.execute("""select user_id from cards where id='%s'""", card_id)
        self.dbh.commit()
        if (users_found > 0):
            user_id = self.cur.fetchone()[0]
            if (is_number(user_id) == False):
                log("Error - No User Found for Card  ID "+str(card_id))
                remote_db.log(card_id,None,"Access Denied - No User")
                return "No user found"
            membership_found = self.cur.execute("""select m.type_id from users as u,memberships as m where u.id=%s AND u.active = 1 AND u.suspend = 0 AND m.user_id = u.id AND m.start < NOW() AND m.end > NOW()""",user_id)
            # Adding commit to make sure transactions are completed (even selects!)
            self.dbh.commit()
            if (membership_found > 0):
                # Found a membership so lets open the door (should actuatlly check the membership types in this result to see if we open the door
                member_type_id = self.cur.fetchone()[0]
                ##### CHECK TO SEE IF THIS USER HAS ACCESS TO THIS NODE
                
                # Access granted, log to database
                if (remote_db != None):
                    remote_db.log(card_id,user_id,"Access Granted")
                return True
            else:
                logger.info("Error - No Membership found for user id "+str(user_id))
                remote_db.log(card_id,user_id,"Access Denied - No Membership")
                return "Membership not found"
        else:
            logger.info("Error - No User Found for Card  ID "+str(card_id))
            remote_db.log(card_id,None,"Access Denied - No User")
            return "No user found"    
        return False
    
    def add_card(self,card_serial,card_hash):
        # Add new card to database
        self.cur.execute("""insert into cards values(NULL,NULL,%s,%s,%s,0,0,NULL)""",("New Card #"+card_serial,card_serial,card_hash))
        self.dbh.commit()
        # Log new card being added
        cardId = self.cur.lastrowid
        logger.info("Card added! id="+str(cardId)+" serial="+card_serial+" hash="+card_hash)
        # Log this to db
        self.log(cardId,None,'Card Added','CARD_ADD')
        
    def update_hash(self,card_id,new_hash, fault=0):
        update_data = "update cards set hash='%s',fault='%s' where id='%s'" % (new_hash,fault,card_id)
        if(self.check()):
            try:
                self.cur.execute(update_data)
                self.dbh.commit()
            except Exception as e:
                logger.info("Failed to update hash, error=%s" % str(e))
                self.cache_sql(update_data)
        else:
            # Save update to sql cache
            self.cache_sql(update_data)
    
    #### Private Functions
    def cache_sql(self,sql):
        try:
            fh = open(self.sqlCacheFile,'a')
            fh.write(sql+"\n")
            fh.close()
        except:
            logger.info("Failed to write SQL To Cache file")
            logger.info(sql)
    
    def push_cache_commands(self):
        if (os.path.isfile(self.sqlCacheFile)):
            try:
                fh = open(self.sqlCacheFile,'r')
                sql_cmds = fh.readlines()
                fh.close()
            except:
                logger.info("Failed to read SQL cache file")
                return
            try:
                for sql_cmd in sql_cmds:
                    self.cur.execute(sql_cmd)
                self.dbh.commit()
            except:
                logger.info("Failed to push SQL commands to database")
                return
            try:
                os.remove(self.sqlCacheFile)
            except:
                logger.info("Failed to delete SQL cache file")
    
