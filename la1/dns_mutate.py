#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch, Controller
import os
import time


Switch = OVSKernelSwitch
result_dir = ""

def create_topo():
	hosts = []

	net = Mininet( controller=RemoteController, switch=Switch, autoSetMacs=True, autoStaticArp=True) ##autoSetMacs must be True for 00:00:00:00:XX as in the ARP resolver.
	controller = net.addController (name = 'Binh_Controller', controller = RemoteController)
	for i in range (1,4):
		hosts.append(net.addHost(name = "h%d"%i, ip = "10.0.0.%d"%i ))
	switch = net.addSwitch(name = 's4', defaultIp="127.0.0.1", listenPort=6634) ###don't forget listenPort!
	
	for h in hosts:
		switch.linkTo(h)

	switch.start([controller])
	controller.start()
	net.start()
	return net

def do_ping(net):
	atk_1 = net.hosts[0]
	atk_2 = net.hosts[1]
	protected_host = net.hosts[2]
	switches = net.switches
	
	print "Start tcpdumps ...\n"
	atk_1.cmd("tcpdump -X -i h1-eth0 > "+result_dir+"atk_1.tcpdump 2>&1 &")
	atk_2.cmd("tcpdump -X -i h2-eth0 > "+result_dir+"atk_2.tcpdump 2>&1 &")
	protected_host.cmd("tcpdump -X -i h3-eth0 > "+result_dir+"protected_host.tcpdump 2>&1 &")
	time.sleep(2)	#wait for tcpdumps
	print "Attacker 1 pinging the protected host: h1 ping -c 5 \"target\" ...\n"
	atk_1.cmd("ping -n -c 5 \"target\" > "+result_dir+"atk_1_ping.result")
	print "Attacker 2 pinging the protected host: h2 ping -c 5 \"target\" ...\n"
	atk_2.cmd("ping -n -c 5 \"target\" > "+result_dir+"atk_2_ping.result")
	switches[0].cmd("dpctl dump-flows tcp:127.0.0.1:6634 > "+result_dir+"flow-table.info")
	time.sleep(2)	#wait for dpctl
	net.stop()

if __name__ == "__main__":
	result_dir = os.getcwd()+"/result/"
	if not os.path.exists(result_dir):
		os.makedirs(result_dir)
	do_ping(create_topo())
	

