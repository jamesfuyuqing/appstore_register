#!/usr/bin/env bash

nowip=`curl -s --connect-timeout 5 http://members.3322.org/dyndns/getip`
/usr/sbin/pppoe-stop
sleep 4
/usr/sbin/pppoe-start
sleep 4
swichend=`curl -s --connect-timeout 5 http://members.3322.org/dyndns/getip`
if [[ ${nowip} == ${swichend} ]]; then
    echo "IP swich Failed"
else
    echo "${nowip}---->${swichend}"
fi
