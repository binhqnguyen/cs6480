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
import subprocess
import commands


BLOCK_COUNT=100 #number of blocks to write to disk.
#IDLE_PERIOD=2*float(BLOCK_COUNT)*1000.0/60000 #time of idle period in seconds.
IDLE_PERIOD=3
if __name__ == "__main__":
	if len(sys.argv) != 2:
		print "Usage: ./receiver.py <writing-pattern (e.g.,1001)>"		
		sys.exit()
	write_pattern = list(sys.argv[1])
	
	#var = raw_input("Start writing? ")
	#if var == "n":
	#	sys.exit()
	#Sender idles or writes to disk based on the write_pattern.
	for i in write_pattern:
		#idle
		if i == '0':
			#print "SENDER %s : idles for %d seconds ..." % (time.strftime("%H:%M:%S"), IDLE_PERIOD)
			print "SENDER %s : writing 0 ..." % (time.strftime("%H:%M:%S"))
			time.sleep(IDLE_PERIOD)
		#writing to disk
		if i == '1':
			#dd_output = subprocess.check_output("time sudo dd if=/dev/zero of=/dev/xvda2 bs=1000k count=20 conv=fdatasync", shell=True)
			status, dd_output = commands.getstatusoutput("sudo dd if=/dev/zero of=/dev/xvda2 bs=1000k count=%s conv=fdatasync" % BLOCK_COUNT)
			#print "%s SENDER writes: write time = %s s , speed= %s MB/s" % (time.strftime("%H:%M:%S"), dd_output[-21:-13], dd_output[-9:-5]) 
			print "SENDER %s : writing 1 ..." % (time.strftime("%H:%M:%S")) 
	
	print "SENDER %s : finished writing %s. Exit" % (time.strftime("%H:%M:%S"), str(write_pattern))
	
