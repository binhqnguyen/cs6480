#!/bin/bash

######Listener#######
echo "======================="
echo "Coresider listening to disk performance ..."
echo "======================="
sum=0
cnt=0
avg=0
while :
do
	OUT=$(sudo hdparm -t /dev/xvda2 | awk '{print d, $11, $12}' "d=$(date +"%T")")
		
	if [ "$OUT" == *MB/sec* ]; then
		OIFS="$IFS"
		IFS=' '
		read -a perf <<< "${OUT}"
		IFS="$OIFS"
		echo ${perf[2]}
		let sum=sum+${perf[2]}
		let cnt=cnt+1
		let avg=sum/cnt
		echo "avg=$avg"	
	fi
done



if [ "$1" == "" ]; then
	echo "Usage: ./coresidency_check <name of VMs host> <name of trigger host>"
fi 

CORESIDENCY_HOST="$PC_NAME.emulab.net"
TRIGGER_HOST="pcxxx.emulab.net"

echo "======================="
echo "Logging into the receiver ..."
echo "======================="
ssh -p 33850 CORESIDENCY_HOST


echo "======================="
echo "Installing apache server on receiver ..."
echo "======================="
sudo apt-get install apache2
sudo /etc/init.d/apache2 start
sudo service apache2 status

echo "Verifying port 80 is open:"
sudo netstat -tulpn | grep :80

echo "======================="
echo "Installing static webpage for apache server to /var/www/..."
echo "======================="
sudo cp <xx.html> /var/www/

echo "Logging out of receiver..."
logout

#############Done with receiver############


#############Doing stuff on the traffic trigger############
echo "======================="
echo "Logging into the web traffic trigger ..."
echo "======================="
ssh TRIGGER_HOST

echo "Installing sun-java6-jdk"
sudo apt-get install python-software-properties
sudo apt-get install software-properties-common
sudo add-apt-repository ppa:webupd8team/java
sudo apt-get update && sudo apt-get install oracle-java6-installer



echo "Installing jmeter on traffic trigger ...."
sudo apt-get update
sudo apt-get jmeter


echo "Trigger running load testing...."
#TODO: jmeter runs 100 threads testing http gets.
#http://jmeter.apache.org/usermanual/get-started.html

echo "Logging out of traffic trigger..."
logout

#############Doing monitoring on the coresider############
echo "======================="
echo "Logging into the coresider ..."
echo "======================="
ssh -p 33850 CORESIDENCY_HOST




