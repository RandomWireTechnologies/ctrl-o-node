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

