ctrl-o-node
===========

This is the python code that runs on the Ctrl-O Nodes

## Setup


* Run ./install.sh
 * This should build and install all dependencies
* ./install.py or python install.py
 * Follow instructions for initializing Pi config
* Sign client-req.pem with master CA from server
* scp ca-cert.pem from server
* sudo mv client*.pem /etc/mysql/

## Local Door Commands

* To initialize a card you need to:
 * Login to pi
 * cd /opt/nfc/doorcmds/
 * Determine your user_id from database
 * echo <user_id> > init (example if your user_id=3 "echo 3 > init")
 * Once the reader LED goes purple, hold a new card to the reader until the LED turns off
 * Check the Node under the Admin controls to see the new card's entry in the database
 * Rename and associate the card with appropriate person and enable if appropriate