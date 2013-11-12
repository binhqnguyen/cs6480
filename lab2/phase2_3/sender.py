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


BLOCK_COUNT=150 #number of blocks to write to disk.
IDLE_PERIOD=4 #idles time in writing 0
INTV=2 #receiver reads disk for each INTV seconds.

if __name__ == "__main__":
	if len(sys.argv) != 2:
		print "Usage: ./receiver.py <writing-pattern (e.g.,1001)>"		
		sys.exit()
	write_pattern = list(sys.argv[1])
	
	#Sender idles or writes to disk based on the write_pattern.
	for i in write_pattern:
		second = time.strftime("%S")
		#print "t=%s" %second
		while second % INTV != 0:
			second = time.strftime("%S")
			#spining
		#Read once per 2 second.
		#idle
		if i == '0':
			print "SENDER %s : writing 0 ..." % (time.strftime("%H:%M:%S"))
			time.sleep(0.4) #slightly sleep to pass the interval
		#writing to disk
		if i == '1':
			print "SENDER %s : writing 1 ..." % (time.strftime("%H:%M:%S")) 
			#status, dd_output = commands.getstatusoutput("sudo dd if=/dev/xvda2 of=/dev/null bs=1000k count=%s conv=fdatasync" % BLOCK_COUNT)
			status, dd_output = commands.getstatusoutput("sudo dd if=/test/a.mov of=/dev/null conv=fdatasync")
			print dd_output
	
	print "SENDER %s : finished writing %s. Exit" % (time.strftime("%H:%M:%S"), str(write_pattern))
	
