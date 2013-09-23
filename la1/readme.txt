CS 6960 Lab assignment 1 README: SDN host mutation
Binh Nguyen

Package structure
================
1. binh_controller.py: controller and DNS server.
2. run_all: bash script to automate the entire experiment.
3. dns_mutate.py: controls topology creating and hosts pinging. 4. result folder: created after an experiment, store all results.

Requirements
================
1. The DNS nameserver is 10.0.0.10. Please add this nameserver to the /etc/resolv.conf.
2. This runs on POX 0.1.0 (Although it passed the test on POX 0.0.0 also).
Clones the POX by git clone http://www.github.com/noxrepo/pox 3. 
The code of this experiment also locates at: cs6480 repo

Run
================
1. Automated running: cd to the submitted folder and do
sudo ./run all <location of pox.py>.
For example: if the pox.py is in /home/mininet/pox, then the command is sudo ./run all /home/mininet/pox This will: (i) copies binh controller.py to /home/mininet/POX/pox/samples (ii) run the dns mutate.py script to generate results in the result folder.
2. Manual running:
(a) Copy binh controller.py to POX’s samples directory. 
(b) Run sudo ./dns mutate.py.
(c) The results are in result folder.

Results
================
1. *_ping.result: results from the ping terminals. There are two ping results from two attackers, you should see different addresses of the protected host in the two files.
2.*.ṫcpdump: ascii format of tcpdump of hosts.
3. flow-table.info: flow table of the switch obtained by dpctl.
4. binh controller.log: log from the controller (info level).
￼￼￼￼￼￼￼￼￼￼￼
