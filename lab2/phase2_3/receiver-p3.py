#!/usr/bin/python
#####################################################
#- Receiver of convert channel (Phase 3):
#  Additional function: listen each 6 second for 
#  60 second. If 2 HIGHs detected, concludes HIGH for 
#  that 60 second period.
#####################################################

import sys
import time
import subprocess
import commands


HIGH_DETECTION_RUN = 3 #How many times running the HIGH detection measurement.
THRESHOLD = 0.0 #LOW if VALUE <= THRESHOLD * HIGH.
counter=0 #counter to stop the listener after a period of time
INTV=60#receiver reads disk for each INTV seconds.
C_INTV=80
high_cnt = 0
total_speed = 0
res = 0
counter_d = 0


#Run high disk performance detection algorithm
#(As described at the beginning of this file)
#Return: list of <High speed, High d_time>
def high_detection():
	high = 0
	total_speed = 0
	cnt = 0
	print "RECEIVER: Preparing, please wait ... "
	#Run disk writing several times to find the HIGH and LOW threshold 
	#of disk performance.
	for i in range(0,HIGH_DETECTION_RUN):
	        status, hd_output = commands.getstatusoutput("sudo hdparm -t --direct /dev/xvda2 | awk '/Timing/ {print $11}'")
	        #status, hd_output = commands.getstatusoutput("sudo dd if=/dev/zero of=/dev/xvda2 bs=100k count=1000 conv=fdatasync | awk '/Copied/ {print $11}'")
		time.sleep(1)
		#speed = hd_output[-9:-5]
		speed = hd_output
		#print speed
		#check for float number
		try:
			total_speed += float(speed)
		except ValueError:
			pass
		cnt += 1

	#calculate average speed for HIGH/LOW threshold.
	avg_speed = total_speed/cnt
	return avg_speed


if __name__ == "__main__":
	if len(sys.argv) != 3:
		print "Usage: ./receiver.py <low threshold, e.g., 0.7> <slot-duration, e.g.,10>" 		
		sys.exit()
	THRESHOLD = sys.argv[1]
	INTV = int(sys.argv[2])
	
	#Receiver measures disk performance several times to detect HIGH value.
	THOLD = high_detection()* float(THRESHOLD)
	print "LOW/HIGH threshold = %s MB/s " % (THOLD)
	print "Started listening:"
	print "=================="
	while 1:
		second = time.strftime("%S")
		res = 0
		while int(second) % INTV != 0:
			second = time.strftime("%S")
			time.sleep(0.5)
			#spining for the next listening slot
		#Read disk
		for i in range(0,7):
			status, hd_output = commands.getstatusoutput("sudo hdparm -t --direct /dev/xvda2 | awk '/Timing/ {print $11}'")
			OUTPUT = 0 #no I/O detected
			speed = hd_output
			if float(speed) <= float(THOLD):	#detected I/O from sender.
				OUTPUT = 1
				high_cnt += 1

		second = time.strftime("%S")
		while int(second) % INTV != 0:
			second = time.strftime("%S")
			time.sleep(0.5)

		if (high_cnt >=2):
			res = 1
		high_cnt = 0
		print "%s RECEIVER :  OUTPUT = %s." % (time.strftime("%H:%M:%S"), str(res))

		#terminate receiver when it runs for over 50 circles. 
		if counter > 50:
			print "Receiver exits ..."
			break

