#!/usr/bin/python
#####################################################
#  Triggerer: download a big file on the sender
#  to cause I/O
#  Input: Triggering pattern.
#  For example: "1010" means "download-idle-download-idle."
#####################################################

import sys
import time
import subprocess
import commands


IDLE_PERIOD=20 #idles time in writing 0
INTV=60#receiver reads disk for each INTV seconds.
cnt=1
TARGET_FILE="10.1.1.2/TBF"


if __name__ == "__main__":
	if len(sys.argv) != 2:
		print "Usage: ./trigger.py <triggering-pattern (e.g.,1001)>"		
		sys.exit()
	write_pattern = list(sys.argv[1])
	last_state = 0
	#Sender idles or read disk  on the write_pattern.
	for i in write_pattern:
		second = time.strftime("%S")
		print "aaaa"
		while int(second) % INTV != 0:
			second = time.strftime("%S")
			time.sleep(1)
			#spining until next slot
		#idle period, doing nothing.
		if i == '0': 
			print "TRIGGER %s : idle 0 ..." % (time.strftime("%H:%M:%S"))
			if last_state == 1: #kill the last running wget
				status, hd_output = commands.getstatusoutput("sudo pkill wget && sudo rm -f TBF*")
				p.terminate()
			time.sleep(5) #slightly sleep to pass the interval
		#downloading from sender to cause I/O
		if i == '1':
			print "TRIGGER %s : trigerring 1 ..." % (time.strftime("%H:%M:%S")) 
			p = subprocess.Popen(['sudo wget %s%s -P /var/' % (TARGET_FILE,cnt)], shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			cnt += 1
			time.sleep(10) #sleep to pass the interval
		last_state = int(i) #remember the last triggering pattern.
	
	print "SENDER %s : finished writing %s. Exit" % (time.strftime("%H:%M:%S"), str(write_pattern))
	
