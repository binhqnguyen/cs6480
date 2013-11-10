#!/bin/bash

NC_NODE_IP="10.1.1.4"

echo "=========================="
echo "Installing cc node ..."
echo "=========================="
read a
if [ "$a" != "n" ]; then
	./euca.install.ccnode
fi

echo "=========================="
echo "Configurating static network for CC node ..."
echo "=========================="
read a
if [ "$a" != "n" ]; then
	./generate_ifcfg.cc
fi


echo "=========================="
echo "Modifying /etc/eucalyptus/eucalyptus.conf to support Network static mode on CC ..."
echo "=========================="
read a
if [ "$a" != "n" ]; then
	./modify_eucalyptus_conf.cc
fi

echo "=========================="
echo "Starting CC node ..."
echo "=========================="
read a
if [ "$a" != "n" ]; then
	./cc.start
fi

echo "=========================="
echo "Enabling root account for CC node ..."
echo "=========================="
read a
if [ "$a" != "n" ]; then
	./enable_root
fi

echo "=========================="
echo "Registering NC node on CC node ..."
echo "=========================="
read a
if [ "$a" != "n" ]; then
	./nc_s.register "$NC_NODE_IP"
fi
