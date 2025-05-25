#!/bin/bash

# PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

ifconfig monitors down &>> /home/gs/logging.txt
iwconfig monitors channel 6 &>> /home/gs/logging.txt
iwconfig monitors mode monitor &>> /home/gs/logging.txt
ifconfig monitors up &>> /home/gs/logging.txt

sleep 5

/home/gs/sniffer/.venv/bin/python /home/gs/sniffer/sniff2.py &>> /home/gs/logging.txt
