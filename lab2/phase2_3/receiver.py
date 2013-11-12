#!/usr/bin/python
#####################################################
#- Receiver of convert channel:
#- Receiver reads data directly from disk 
#  and measures read bandwidth/time.
#- Receiver detects disk low/high performance and 
#  determines whether sender is writing to disk.
#- On/Off detection:
#  + HIGH: When the receiver starts for the first time, 
#  it will read the disk for several times (when sender is idle). 
#  The average disk performance during this time
#  will be store as HIGH value.
#  + LOW: a ratio threshold is predefined to determine
#  LOW value. For example, any value that is lower than 
#  threshold*HIGHVALUE is detected as LOW.
#####################################################

import sys
import time
import subprocess
import commands


HIGH_DETECTION_RUN = 2 #How many times running the HIGH detection measurement.
THRESHOLD = 0.85 #LOW if VALUE <= THRESHOLD * HIGH.
counter=0 #counter to stop the listener after a period of time
INTV=10#receiver reads disk for each INTV seconds.


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
	        status, hd_output = commands.getstatusoutput("sudo hdparm -t /dev/xvda2 | awk '/Timing/ {print $11}'")
		speed = hd_output
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
		#print "t=%s" %second
		while int(second) % INTV != 0:
			second = time.strftime("%S")
			#spining for the next listening slot
		#Read disk every 10 second
	        status, hd_output = commands.getstatusoutput("sudo hdparm -t /dev/xvda2 | awk '/Timing/ {print $11}'")
		OUTPUT = 0 #no I/O detected
		speed = hd_output
		if float(speed) <= float(THOLD):	#detected I/O from sender.
			OUTPUT = 1
		print "%s RECEIVER : speed= %s MB/s , OUTPUT = %s." % (time.strftime("%H:%M:%S"), str(speed), str(OUTPUT))
		#terminate receiver when it runs for over 50 circles. 
		if counter > 50:
			print "Receiver exits ..."
			break

