#!/bin/bash

HOST="192.168.10.128"
ryu-manager --verbose --ofp-listen-host $HOST /home/cloud/setup/ryu/ryu/app/my_simple_switch_13.py
