#!/bin/bash

iptables -t nat -L
iptables -t nat -F
echo ""
echo ""
iptables -t nat -L
