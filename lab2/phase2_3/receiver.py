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


HIGH_DETECTION_RUN = 5 #How many times running the HIGH detection measurement.
THRESHOLD = 0.85 #LOW if VALUE <= THRESHOLD * HIGH.
BLOCK_COUNT = 15 #number of blocks written to disk to measure I/O
HIGH_TH = 1 #fine-grained to coarse-grained converter
LOW_TH = 1 #fine-grained to coarse-grained converter
#variables used for fine-grained to coarse-grained convertion.
cnt_high = 0
cnt_low = 0
sum_high = 0
sum_low = 0
counter = 0
INTV=2 #receiver reads disk for each INTV seconds.

#Detect coarse low/high from fine-grained disk measurement.
def detect_low_high(OUTPUT,speed):
	global cnt_high
	global cnt_low
	global sum_high
	global sum_low
	global counter
	global HIGH_TH
	
	if int(OUTPUT) == 1:
		cnt_high += 1
		sum_high += float(speed)
	if int(OUTPUT) == 0: 
		cnt_low += 1
		sum_low += float(speed)

	#High detected
	if cnt_high >= HIGH_TH:
		print "%s RECEIVER : speed= %sMB/s, OUTPUT = 1." % (time.strftime("%H:%M:%S"), str(sum_high/cnt_high))
		cnt_high = 0
		sum_high = 0
		counter += 1

	#Low detected, note: to tell a low period, double times of fine grained low period needed
	#since low-period write speed is doubled of high-period write speed. 
	if cnt_low >= LOW_TH:
		print "%s RECEIVER : speed= %sMB/s , OUTPUT = 0." % (time.strftime("%H:%M:%S"), str(sum_low/cnt_low))
		cnt_low = 0
		sum_low = 0
		counter += 1


#Run high disk performance detection algorithm
#(As described at the beginning of this file)
#Return: list of <High speed, High d_time>
def high_detection():
	high = 0
	total_speed = 0
	total_time = 0
	cnt = 0
	print "Receiver is training to determine LOW/HIGH values ..."
	#Run disk writing several times to find the HIGH and LOW threshold 
	#of disk performance.
	for i in range(0,HIGH_DETECTION_RUN):
	        #status, hd_output = commands.getstatusoutput("sudo dd if=/dev/zero of=/dev/xvda2 bs=1000k count=%s conv=fdatasync" % BLOCK_COUNT)
	        status, hd_output = commands.getstatusoutput("sudo dd if=/test/a.mov of=/dev/null conv=fdatasync")
		speed = hd_output[-9:-5]
		d_time = hd_output[-21:-13]
		
		#check for float number
		try:
			total_speed += float(speed)
			total_time += float(d_time)
		except ValueError:
			pass
		cnt += 1

	#calculate average speed for HIGH/LOW threshold.
	avg_speed = total_speed/cnt
	avg_time = total_time/cnt
	
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
	#compute low speed and read time
	lows.append(float(highs[0])*float(THRESHOLD))
	lows.append(float(highs[1])*float(THRESHOLD))
	print "LOW/HIGH threshold = %s MB/s " % (lows[0])
	print "Started listening:"
	print "=================="
	while 1:
	        #status, hd_output = commands.getstatusoutput("sudo dd if=/dev/zero of=/dev/xvda2 bs=1000k count=%s conv=fdatasync" % BLOCK_COUNT)
		second = time.strftime("%S")
		#print "t=%s" %second
		while second % INTV != 0:
			second = time.strftime("%S")
			#spining
		#Read disk every 2 second
		status, hd_output = commands.getstatusoutput("sudo dd if=/test/a.mov of=/dev/null conv=fdatasync")
		OUTPUT = 0 #no I/O detected
		speed = hd_output[-9:-5]
		d_time = hd_output[-21:-13]
		


		#set fine-grained output to 1 if disk performance is bad (or "someone" is writing). 
		if float(speed) <= float(lows[0]):	#detected I/O from sender.
			OUTPUT = 1

		print "%s RECEIVER : speed= %s MB/s , OUTPUT = %s." % (time.strftime("%H:%M:%S"), str(speed), str(OUTPUT))
		#detect_low_high(OUTPUT, speed)
		
		#terminate receiver when it runs for over 50 circles. 
		if counter > 50:
			print "Receiver exits ..."
			break
		
		

