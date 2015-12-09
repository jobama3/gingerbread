#!/bin/bash

cp fcserver.json /usr/local/bin/fcserver.json
pkill fcserver
/usr/local/bin/fcserver /usr/local/bin/fcserver.json >/var/log/fcserver.log 2>&1 &