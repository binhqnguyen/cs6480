#!/usr/bin/python
#####################################################
#- Sender of convert channel:
#- Sender write data to disk to consume disk bandwidth 
#and so receiver can measure disk read bandwidth to 
#detect disk usage.
#- Sender is instructed to write/idle using a binary string.
#  For example: "1010" means "write-idle-write-idle."
#####################################################

import sys
import time
import datetime
import subprocess
import commands


IDLE_PERIOD=5 #time of idle period in seconds.
if __name__ == "__main__":
	if len(sys.argv) != 2:
		print "Usage: ./receiver.py <writing-pattern (e.g.,1001)>"		
		sys.exit()
	write_pattern = list(sys.argv[1])
	
	var = raw_input("Start writing? ")
	if var == "n":
		sys.exit()
	#Sender idles or writes to disk based on the write_pattern.
	for i in write_pattern:
		#idle
		if i == '0':
			print "SENDER %s : idles for %d seconds ..." % (datetime.datetime.now().time(), IDLE_PERIOD)
			print "--------------------------"
			time.sleep(IDLE_PERIOD)
		#writing to disk
		if i == '1':
			#dd_output = subprocess.check_output("time sudo dd if=/dev/zero of=/dev/xvda2 bs=1000k count=20 conv=fdatasync", shell=True)
			status, dd_output = commands.getstatusoutput("sudo dd if=/dev/zero of=/dev/xvda2 bs=1000k count=400 conv=fdatasync | awk '/copied/ {print $6, $8}'")
			print "%s SENDER writes: write time = %s s , speed= %s MB/s" % (datetime.datetime.now().time(), dd_output[-21:-13], dd_output[-9:-5]) 
			print "--------------------------"
	
	
	print "SENDER %s : finished writing %s. Exit" % (datetime.datetime.now().time(), str(write_pattern))
	
