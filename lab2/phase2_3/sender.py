#!/usr/bin/python
#####################################################
#- Sender of convert channel:
#- Sender read from disk to cause I/O 
#- Sender is instructed to read/idle using a binary string.
#  For example: "1010" means "read-idle-read-idle."
#####################################################

import sys
import time
import subprocess
import commands


BLOCK_COUNT=100 #number of blocks to write to disk.
IDLE_PERIOD=4 #idles time in writing 0
INTV=8#receiver reads disk for each INTV seconds.

if __name__ == "__main__":
	if len(sys.argv) != 2:
		print "Usage: ./receiver.py <writing-pattern (e.g.,1001)>"		
		sys.exit()
	write_pattern = list(sys.argv[1])
	
	#Sender idles or read disk  on the write_pattern.
	for i in write_pattern:
		second = time.strftime("%S")
		while int(second) % INTV != 0:
			second = time.strftime("%S")
			#spining until next slot
		#idle
		if i == '0':
			print "SENDER %s : writing 0 ..." % (time.strftime("%H:%M:%S"))
			time.sleep(INTV-0.5) #slightly sleep to pass the interval
		#read from disk, meaning writing 1 to the channel
		if i == '1':
			print "SENDER %s : writing 1 ..." % (time.strftime("%H:%M:%S")) 
			status, hd_output = commands.getstatusoutput("sudo hdparm -t /dev/xvda2 | awk '/Timing/ {print $11}'")
			hd_output
	
	print "SENDER %s : finished writing %s. Exit" % (time.strftime("%H:%M:%S"), str(write_pattern))
	
