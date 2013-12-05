#!/bin/bash
################# Startup ###########################
ovsdb-server --remote=punix:/usr/local/var/run/openvswitch/db.sock \
                     --remote=db:Open_vSwitch,Open_vSwitch,manager_options \
                     --bootstrap-ca-cert=db:Open_vSwitch,SSL,ca_cert \
                     --pidfile --detach
 
ovs-vsctl --no-wait init
ovs-vswitchd --pidfile --detach
