#!/bin/bash

SGW_NET_D="192.168.4.20"
iptables -t nat -A PREROUTING -i eth0 -j DNAT --to $SGW_NET_D
