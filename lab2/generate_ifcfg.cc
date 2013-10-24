#!/bin/bash
#cloud cluster

device_name=$(./phy_intf)

cfg_file=ifcfg-$device_name
echo "Creating $cfg_file.cc ..."

echo "DEVICE=$device_name
BOOTPROTO=static
IPADDR=10.1.1.3
NETMASK=255.255.255.0
ONBOOT=yes" > $cfg_file

echo "Copying $cfg_file to /etc/sysconfig/network-scripts ..."
sudo cp $cfg_file $cfg_file.cc
sudo mv $cfg_file /etc/sysconfig/network-scripts/

echo "Restarting service network..."
sudo service network restart
 
