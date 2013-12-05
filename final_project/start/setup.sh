#!/bin/bash

./net/net_d.sh
ovs-vsctl add-br br0 
ovs-vsctl add-port br0 net_d
ovs-vsctl add-port br0 net_cloud
#ovs-vsctl add-port br0 eth2
ovs-vsctl set-controller br0 tcp:192.168.4.100:6633

#for i in 1 2 3 4; do
#ovs-vsctl add-port br0 p$i -- set Interface p$i ofport_request=$i
#ovs-ofctl mod-port br0 p$i up
#done

ovs-vsctl show
ovs-ofctl show br0
