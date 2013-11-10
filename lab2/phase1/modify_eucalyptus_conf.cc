#!/bin/bash

NC_INF=$(./phy_intf)

echo "Modifying eucalyptus.conf.cc file ... VNET_PRIVIINTERFACE=$NC_INF"
sudo perl -pi -e "s/VNET_PRIVINTERFACE.*/VNET_PRIVINTERFACE=\"$NC_INF\"/g" eucalyptus.conf.cc

echo "Copying eucalyptuc.conf.cc to /etc/eucalyptus/  ..."
sudo cp eucalyptus.conf.cc /etc/eucalyptus/eucalyptus.conf
 
echo "Changing permission for /var/run/eucalyptus/net"
sudo chmod 0777 /var/run/eucalyptus/net


