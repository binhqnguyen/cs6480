# Copyright (C) 2011 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet


# JUNGUK
from ryu.lib.packet import ipv4
from ryu.lib.packet import arp 
from ryu.lib.packet import sctp
from ryu.lib.packet import icmp
from ryu.lib.packet import udp
from ryu.lib.packet import gtp
from ryu.ofproto import ether

GTP_PORT = 2152

enodeb_net_d_mac = "00:0c:29:42:72:d0"
enodeb_net_d_ip = "192.168.4.90"

sgw_net_d_mac = "00:0c:29:55:42:03"
sgw_net_d_ip = "192.168.4.20"

ovs_net_cloud_mac = "00:0c:29:70:12:36" #eth1 in ovs 
ovs_net_cloud_ip = "192.168.10.128"

ol_net_server_mac = "00:0c:29:29:f9:66"
ol_net_server_ip = "192.168.8.101"

ovs_net_server_mac = "00:0c:29:70:12:40" #eth2 in ovs
ovs_net_server_ip = "192.168.8.128"


class OvsPort (object):
    def __init__(self, mac, ip, port):
        self.mac = mac
        self.ip = ip
        self.port = port

class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
		# define each port, enodeb, and server 
        self.enodeb = OvsPort(enodeb_net_d_mac, enodeb_net_d_ip, 1)
        self.ovs_net_d = OvsPort(sgw_net_d_mac , sgw_net_d_ip, 1)
        self.ovs_net_cloud = OvsPort(ovs_net_cloud_mac, ovs_net_cloud_ip, 2)
        self.cloud = OvsPort(ol_net_server_mac, ol_net_server_ip, 2)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install table-miss flow entry
        #
        # We specify NO BUFFER to max_len of the output action due to
        # OVS bug. At this moment, if we specify a lesser number, e.g.,
        # 128, OVS will send Packet-In with invalid buffer_id and
        # truncated packet data. In that case, we cannot output packets
        # correctly.
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]

        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                match=match, instructions=inst)
        datapath.send_msg(mod)
   
    def decap_packet(self, eth, ipv4, icmp_packet):
	p = packet.Packet()
	p.add_protocol(eth)
	p.add_protocol(ipv4)
	p.add_protocol(icmp_packet)
	p.serialize()
	return p.data
    
	
    def gtp_encap(self,eth, ip_packet, upd_packet, gtp_packet):
	p = packet.Packet()
	p.add_protocol(eth)
	p.add_protocol(ip_packet)
	p.add_protocol(udp_packet)
	p.add_protocol(gtp_packet)
	p.serialize()
	return p.data
    
    def create_arp(self, arp_packet, eth):
	p = packet.Packet()
	p.add_protocol(eth)
	p.add_protocol(arp_packet)
	print p
	p.serialize()
	return p.data
		

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        dst = eth.dst
        src = eth.src

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        #self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

	
	ip_packet = packet.Packet(msg.data).get_protocols(ipv4.ipv4)
	if ip_packet:
		print "ip_packet[0].src=%s, ip_packet[0].dst=%s"%(ip_packet[0].src,ip_packet[0].dst)
		if ip_packet[0].src == ol_net_server_ip: ##packets from offloading server.
			print "***********To ovs..."
			if up_ip_packet:
				eth_packet = ether.ethernet (enodeb_net_d_mac, sgw_net_d_mac, 0x0800)
				icmp_packet = packet.Packet(msg.data).get_protocols(icmp.icmp)
				inner_ip_packet = 
				udp_packet 
				gtp_u
				gtp ...
				###gtp = [eth, outer_ip, udp with 2152, gtp_u with teid and length, tinner ip]
				up_ip_packet[0].src =  #enb-sgw IPs
				up_ip_packet[1] #UE-google.com IPs.
				data = self.gtp_encap(eth, ip_packet[1], upd_packet, gtp_packet)
				out_port = 2	#outport is the port to ovs
				actions = [parser.OFPActionOutput(out_port)]
				out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port, actions=actions, data=data)
				datapath.send_msg(out)
				print "Sending packet to port %d " % out_port
				print "##############"
				return



	if packet.Packet(msg.data).get_protocol(udp.udp):
		udp_packet = packet.Packet(msg.data).get_protocols(udp.udp)
		up_ip_packet = ip_packet

		if udp_packet and udp_packet[0].dst_port == GTP_PORT: #GTP-U packet
			print "############################################"
			print "ip_packet[1].src=%s, ip_packet[1].dst=%s"%(ip_packet[1].src,ip_packet[1].dst)

			print "packet in: in_port=%d eth.dst = %s  eth.src = %s  dpid = %d  outport = %d" % (in_port,str(dst),str(src),dpid,out_port)
			print "udp.src_port=%s, udp.dst_port=%s"%(udp_packet[0].src_port,udp_packet[0].dst_port)
			gtp_packet = packet.Packet(msg.data).get_protocol(gtp.gtp)

			print "Gtp.flag=%s, .msg_type=%s, .total_length=%s, .teid=%s" % (str(gtp_packet.flag), str(gtp_packet.msg_type), str(gtp_packet.total_length), str (gtp_packet.teid))
			if packet.Packet(msg.data).get_protocol(icmp.icmp):
				icmp_packet = packet.Packet(msg.data).get_protocol(icmp.icmp)
				#print len(icmp_packet.data)
				#e = ethernet.ethernet(arp_packet.src_mac, target.mac, ether.ETH_TYPE_ARP)	
				#print ip_packet
				if ip_packet[1]:
					print "*****To offloading..."
					eth.src = ovs_net_server_mac
					eth.dst = ol_net_server_mac 
					ip_packet[1].src = ovs_net_server_ip #change IP src/dst adds to ovs/ols.
					ip_packet[1].dst = ol_net_server_ip
					data = self.decap_packet(eth, ip_packet[1], icmp_packet) #build a ICMP packet.
					out_port = 3	#out port is the port to ols.
					actions = [parser.OFPActionOutput(out_port)]
					out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port, actions=actions, data=data)
					datapath.send_msg(out)
					print "Sending packet to port %d " % out_port
					print "##############"
					return
	'''
	if packet.Packet(msg.data).get_protocol(arp.arp): #received arp packets
		arp_packet = packet.Packet(msg.data).get_protocols(arp.arp)[0]
		src_mac = ""
		dst_mac = ""
		old_src_ip = arp_packet.src_ip
		if arp_packet.dst_ip == ovs_net_cloud_ip:
			print "ARP replying %s ..." % ovs_net_cloud_ip 
			arp_packet.dst_mac = arp_packet.src_mac
			arp_packet.src_mac = ovs_net_cloud_mac #eth1 in ovs 
			arp_packet.src_ip = ovs_net_cloud_ip
			arp_packet.dst_ip = "192.168.4.90"
		if arp_packet.dst_ip == ovs_net_server_ip:
			print "ARP replying %s ..." % ovs_net_server_ip 
			arp_packet.dst_mac = arp_packet.src_mac
			arp_packet.src_mac = ovs_net_server_mac #eth2 in ovs 
			arp_packet.src_ip = ovs_net_server_ip
			arp_packet.dst_ip = old_src_ip
			
	
		eth.src = arp_packet.src_mac
		eth.dst = arp_packet.dst_mac
		arp_packet.opcode = arp.ARP_REPLY
		data = self.create_arp(arp_packet, eth)
	'''	
 	actions = [parser.OFPActionOutput(out_port)]
        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
            self.add_flow(datapath, 1, match, actions)

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)


	'''
	# install a flow to avoid packet_in next time
	'''
	'''
	if out_port != ofproto.OFPP_FLOOD:
		match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
		self.add_flow(datapath, 1, match, actions)
	'''
	'''
	data = None
	if msg.buffer_id == ofproto.OFP_NO_BUFFER:
		data = msg.data

	out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
							  in_port=in_port, actions=actions, data=data)

	print "Sending out port=%s" % out_port
	datapath.send_msg(out)
	'''
