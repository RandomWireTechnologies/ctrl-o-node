#!/bin/sh

if [ -f localMySQLbackup.sql ]; then
	mysql --defaults-file=mysql_config -e "slave stop;reset slave;"
	mysql --defaults-file=mysql_config < localMySQLbackup.sql
	mysql --defaults-file=mysql_config -e "slave start"
fi
