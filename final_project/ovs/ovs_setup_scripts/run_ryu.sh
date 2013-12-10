#!/bin/bash
ovs_ip="192.168.10.128"

if [ "$1" == "" ]; then
	echo "Usage: <path to ryu controller code>"
	exit
fi

ryu-manager --verbose --ofp-listen-host $ovs_ip $1


