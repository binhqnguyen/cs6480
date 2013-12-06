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

	
	if packet.Packet(msg.data).get_protocol(udp.udp):
		ip_packet = packet.Packet(msg.data).get_protocols(ipv4.ipv4)
		udp_packet = packet.Packet(msg.data).get_protocols(udp.udp)
		if udp_packet and udp_packet[0].dst_port == GTP_PORT: #GTP-U packet
			print "############################################"
			print "ip_packet[0].src=%s, ip_packet[0].dst=%s"%(ip_packet[0].src,ip_packet[0].dst)
			print "ip_packet[1].src=%s, ip_packet[1].dst=%s"%(ip_packet[1].src,ip_packet[1].dst)

			print "packet in: in_port=%d eth.dst = %s  eth.src = %s  dpid = %d  outport = %d" % (in_port,str(dst),str(src),dpid,out_port)
			print "udp.src_port=%s, udp.dst_port=%s"%(udp_packet[0].src_port,udp_packet[0].dst_port)
			gtp_packet = packet.Packet(msg.data).get_protocol(gtp.gtp)

			print "Gtp.flag=%s, .msg_type=%s, .total_length=%s, .teid=%s" % (str(gtp_packet.flag), str(gtp_packet.msg_type), str(gtp_packet.total_length), str (gtp_packet.teid))
			if packet.Packet(msg.data).get_protocol(icmp.icmp):
				icmp_packet = packet.Packet(msg.data).get_protocol(icmp.icmp)
				#print len(icmp_packet.data)
				#e = ethernet.ethernet(arp_packet.src_mac, target.mac, ether.ETH_TYPE_ARP)	
				print ip_packet
				eth.src = ovs_net_server_mac
				eth.dst = ol_net_server_mac 
				if ip_packet[1]:
					ip_packet[1].src = ovs_net_server_ip
					ip_packet[1].dst = ol_net_server_ip
					#echo = icmp.echo(id_=66, seq=1)
					#ping = icmp.icmp(icmp.ICMP_ECHO_REQUEST,code=0, csum=0, data=echo)
					data = self.decap_packet(eth, ip_packet[1], icmp_packet) 
					out_port = 3
					actions = [parser.OFPActionOutput(out_port)]
					out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port, actions=actions, data=data)
					datapath.send_msg(out)
					print "Sending packet to port %d " % out_port
					print "##############"
					return

	print "Received uninterested packet, broadcasting to 2 and 3..."
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
