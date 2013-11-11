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


HIGH_DETECTION_RUN=2 #How many times running the HIGH detection measurement.
THRESHOLD=0.7 #LOW if VALUE <= THRESHOLD * HIGH.

#Run high disk performance detection algorithm
#(As described at the beginning of this file)
#Return: list of <High speed, High d_time>
def high_detection():
	high = 0
	total_speed = 0
	total_time = 0
	for i in range(0,HIGH_DETECTION_RUN):
		#Read disk performance using hdparm
		status, hd_output = commands.getstatusoutput("sudo hdparm -t --direct /dev/xvda2 | awk '/Timing/ {print $8,$11}'")	
		d_time = hd_output.split(" ")[0]
		speed = hd_output.split(" ")[1]
		print "%s RECEIVER: write time = %s s , speed= %s MB/s" % (time.strftime("%H:%M:%S"), d_time, speed) 
		try:
			total_speed += float(speed)
			total_time += float(d_time)
		except ValueError:
			pass
	avg_speed = total_speed/HIGH_DETECTION_RUN
	avg_time = total_time/HIGH_DETECTION_RUN
	
	print "RECEIVER %s : High speed= %s , high time= %s ." % (time.strftime("%H:%M:%S"), str(avg_speed), str(avg_time))
	return_list = []
	return_list.append(avg_speed)
	return_list.append(avg_time)
	return return_list
	
if __name__ == "__main__":
	if len(sys.argv) != 2:
		print "Usage: ./receiver.py <low threshold, e.g., 0.7>"		
		sys.exit()
	THRESHOLD = sys.argv[1]
	
	#Receiver measures disk performance several times to detect HIGH value.
	highs = []
	lows = []
	highs = high_detection()
	print "%s %s %s" % (highs[0],highs[1], THRESHOLD)
	#compute low speed and read time
	print "LOW = %s, %s " % (highs[0]*float(THRESHOLD), highs[1]*float(THRESHOLD))
	lows.append(float(highs[0])*float(THRESHOLD))
	lows.append(float(highs[1])*float(THRESHOLD))
	
        var = raw_input("Start listening? ")
        if var == "n":
                sys.exit()
	#Receiver keeps listening to sender and prints out low/high values.
	while 1:
		status, hd_output = commands.getstatusoutput("sudo hdparm -t --direct /dev/xvda2 | awk '/Timing/ {print $8,$11}'")	
		OUTPUT = 0 #no I/O detected
		d_time = hd_output.split(" ")[0]
		speed = hd_output.split(" ")[1]

		print "%s %s" % (speed, float(lows[0]))
		if speed <= float(lows[0]):	#detected I/O from sender.
			OUTPUT = 1
		print "RECEIVER %s : speed= %s , time= %s , OUTPUT = %s ." % (time.strftime("%H:%M:%S"), str(speed), str(d_time), str(OUTPUT))

		

