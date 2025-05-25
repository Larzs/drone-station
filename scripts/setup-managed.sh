#!/bin/bash
PATH=/usr/sbin:/usr/bin:/sbin:/bin

ifconfig wlan0 down
iwconfig wlan0 channel 1
iwconfig wlan0 mode managed
ifconfig wlan0 up

service NetworkManager start
