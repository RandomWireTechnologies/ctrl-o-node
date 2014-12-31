#!/bin/sh

if [ ! -f /usr/local/bin/beep ]; then
        sudo cp beep.sh /usr/local/bin/beep
fi
if [ ! -f config.py ] ;then
        cp config_template.py config.py
fi
if [ ! -f mifare_key.h ]; then
        cp mifare_key_template.h mifare_key.h
fi
if [ -d /etc/monit ]; then
        if [ ! -f /etc/monit/monitrc ]; then
                sudo cp monitrc_template /etc/monit/monitrc
        fi
fi
if [ ! -f mysql_config ]; then
        sudo cp mysql_config_template mysql_config
        sudo chmod 700 mysql_config
fi
if [ ! -f /etc/init.d/nfc ]; then
        sudo cp nfc.init.d /etc/init.d/nfc
fi
if [ -d build ]; then
        rm -rf build
fi
./pbuild.sh

