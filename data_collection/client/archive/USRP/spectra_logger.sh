#!/bin/bash

#until ping -c1 192.168.10.2 &>/dev/null; do
#	sleep 1;
#	python /home/zerina/data_logger.py >> /home/zerina/log.txt
#	echo "Logger is running";
#done 
printf "Pinging Host"
while ! timeout 0.2 ping -c 1 -n 192.168.10.2 &>/dev/null
do
	printf "Searching"
done

cd /home/zerina & python ./data_logger.py

