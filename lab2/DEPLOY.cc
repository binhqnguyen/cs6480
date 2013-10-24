#!/bin/bash

NC_NODE_IP="10.1.1.4"

echo "=========================="
echo "Installing cc node ..."
echo "=========================="

./euca.install.ccnode

echo "=========================="
echo "Configurating static network for CC node ..."
echo "=========================="

./generate_ifcfg.cc

echo "=========================="
echo "Starting CC node ..."
echo "=========================="

./cc.start

echo "=========================="
echo "Enabling root account for CC node ..."
echo "=========================="

./enable_root

echo "=========================="
echo "Registering NC node on CC node ..."
echo "=========================="

./nc_s.register "$NC_NODE_IP"
