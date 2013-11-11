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


HIGH_DETECTION_RUN=5 #How many times running the HIGH detection measurement.
THRESHOLD=0.85 #LOW if VALUE <= THRESHOLD * HIGH.
BLOCK_COUNT=10 #number of blocks written to disk to measure I/O
freeze = 0
last_finegrain = 0
finegrain_out = {}
cnt_high = 0
cnt_low = 0
sum_high = 0
sum_low = 0
counter = 0
HIGH_TH = 6
LOW_TH = 12

#Detect coarse low/high from fine-grained disk measurement.
def detect_low_high(OUTPUT,speed):
	global cnt_high
	global cnt_low
	global sum_high
	global sum_low
	global freeze
	global last_finegrain
	global finegrain_out
	global counter
	global HIGH_TH
	
	finegrain_out[speed] = OUTPUT
	#print "sp=%s output=%s last_fg=%s cnt_high=%s cnt_low=%s free=%s" % (speed, OUTPUT, last_finegrain, cnt_high, cnt_low, freeze)
	#Switching detected, likely change has happened.
	#If so unfreeze the counter.
	#print "%s %s" % (speed, OUTPUT)
	if int(OUTPUT) != last_finegrain :
		freeze = 0
	if int(OUTPUT) == 1 and freeze != 1:
		cnt_high += 1
		sum_high += float(speed)
	if int(OUTPUT) == 0 and freeze != 1: 
		cnt_low += 1
		sum_low += float(speed)
	#High detected
	if cnt_high >= HIGH_TH:
		#freeze = 1	#no long count for high
		print "%s RECEIVER : speed= %sMB/s, OUTPUT = 1." % (time.strftime("%H:%M:%S"), str(sum_high/cnt_high))
		cnt_high = 0
		sum_high = 0
		counter += 1
	#Low detected, note: to tell a low period, double times of fine grained low period needed
	#since low-period write speed is doubled of high-period write speed. 
	if cnt_low >= LOW_TH:
		#freeze = 1
		print "%s RECEIVER : speed= %sMB/s , OUTPUT = 0." % (time.strftime("%H:%M:%S"), str(sum_low/cnt_low))
		cnt_low = 0
		sum_low = 0
		counter += 1
	last_finegrain = int(OUTPUT)

#Run high disk performance detection algorithm
#(As described at the beginning of this file)
#Return: list of <High speed, High d_time>
def high_detection():
	high = 0
	total_speed = 0
	total_time = 0
	cnt = 0
	print "Receiver is training to determine LOW/HIGH values ..."
	for i in range(0,HIGH_DETECTION_RUN):
		#Read disk performance using hdparm
		#status, hd_output = commands.getstatusoutput("sudo hdparm -t --direct /dev/xvda2 | awk '/Timing/ {print $8,$11}'")	
		#status, hd_output = commands.getstatusoutput("sudo dd if=/dev/zero of=/dev/xvda2 bs=1000k count=400 conv=fdatasync | awk '/copied/ {print $6, $8}'")
	        status, hd_output = commands.getstatusoutput("sudo dd if=/dev/zero of=/dev/xvda2 bs=1000k count=%s conv=fdatasync" % BLOCK_COUNT)
		#d_time = hd_output.split(" ")[0]
		#speed = hd_output.split(" ")[1]
		speed = hd_output[-9:-5]
		d_time = hd_output[-21:-13]

		#print "%s RECEIVER: write time = %s s , speed= %s MB/s" % (time.strftime("%H:%M:%S"), d_time, speed) 
		try:
			total_speed += float(speed)
			total_time += float(d_time)
		except ValueError:
			pass
		cnt += 1
	avg_speed = total_speed/cnt
	avg_time = total_time/cnt
	
	#print "RECEIVER %s : High speed= %s , high time= %s ." % (time.strftime("%H:%M:%S"), str(avg_speed), str(avg_time))
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
	print "Training finished, High threshold= %s MB/s, low threshold =%s MB/s " % (highs[0],lows[0])
	print "Started listening:"
	print "=================="
        #var = raw_input("Start listening? ")
        #if var == "n":
        #        sys.exit()
	#Receiver keeps listening to sender and prints out low/high values.
	while 1:
		#status, hd_output = commands.getstatusoutput("sudo hdparm -t --direct /dev/xvda2 | awk '/Timing/ {print $8,$11}'")	
		#status, hd_output = commands.getstatusoutput("sudo dd if=/dev/zero of=/dev/xvda2 bs=1000k count=300 conv=fdatasync | awk '/copied/ {print $6, $8}'")
	        status, hd_output = commands.getstatusoutput("sudo dd if=/dev/zero of=/dev/xvda2 bs=1000k count=%s conv=fdatasync" % BLOCK_COUNT)
		OUTPUT = 0 #no I/O detected
		#d_time = hd_output.split(" ")[0]
		#speed = hd_output.split(" ")[1]
		speed = hd_output[-9:-5]
		d_time = hd_output[-21:-13]

		#print "%s %s" % (speed, float(lows[0]))
		if float(speed) <= float(lows[0]):	#detected I/O from sender.
			OUTPUT = 1
		#print "%s RECEIVER : speed= %s , OUTPUT = %s ." % (time.strftime("%H:%M:%S"), str(speed), str(OUTPUT))
		detect_low_high(OUTPUT, speed)
		
		if counter > 50:
			break
		
	#print finegrain_output
		

