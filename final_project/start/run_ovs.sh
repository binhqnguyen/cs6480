#!/bin/bash

#!/bin/bash

modprobe -r openvswitch.ko
modprobe gre
modprobe libcrc32c
insmod /home/cloud/setup/openvswitch-2.0.0/datapath/linux/openvswitch.ko
 
################# Startup ###########################
ovsdb-server --remote=punix:/usr/local/var/run/openvswitch/db.sock \
                     --remote=db:Open_vSwitch,Open_vSwitch,manager_options \
                     --private-key=db:Open_vSwitch,SSL,private_key \
                     --certificate=db:Open_vSwitch,SSL,certificate \
                     --bootstrap-ca-cert=db:Open_vSwitch,SSL,ca_cert \
                     --pidfile --detach
 
ovs-vsctl --no-wait init
ovs-vswitchd --pidfile --detach
