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

ovs_net_d_mac = "00:0c:29:70:12:4a"
ovs_net_d_ip = "192.168.4.101"

ovs_net_cloud_mac = "00:0c:29:70:12:36" #eth1 in ovs 
ovs_net_cloud_ip = "192.168.10.128"

ol_net_server_mac = "00:0c:29:29:f9:66"
ol_net_server_ip = "192.168.8.129"

ovs_net_server_mac = "00:0c:29:70:12:40" #eth2 in ovs
ovs_net_server_ip = "192.168.8.128"

ENODEB_TEID = 21


class OvsPort (object):
    def __init__(self, mac, ip, port):
        self.mac = mac
        self.ip = ip
        self.port = port
        self.uplink_udp = None	#outer Udp header of GTP packets
        self.uplink_gtp_header = None	#outer GTP header
        self.uplink_ipv4 = None		#outer ipv4 header
        self.uplink_eth = None	#outer ethernet header 
        self.uplink_inner_ipv4 = None		#inner ipv4 header

class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
		# define each port, enodeb, and server 
        self.enodeb = OvsPort(enodeb_net_d_mac, enodeb_net_d_ip, 2)
        self.ovs_net_d = OvsPort(sgw_net_d_mac , sgw_net_d_ip, 1)
        self.ovs_net_cloud = OvsPort(ovs_net_cloud_mac, ovs_net_cloud_ip, 2)
        self.ovs_net_server = OvsPort(ovs_net_server_mac, ovs_net_server_ip, 3)
        self.cloud_net_server = OvsPort(ol_net_server_mac, ol_net_server_ip, 1)

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
   
    def _create_icmp(self, eth, ipv4, icmp_packet):
		p = packet.Packet()
		p.add_protocol(eth)
		p.add_protocol(ipv4)
		p.add_protocol(icmp_packet)
		p.serialize()
		return p.data

	#generate a packet using packet.add_protocol(packet)
	#protocols: a list of headers that used to build the packet.
    def _generate_packet(self, protocols):
		p = packet.Packet()
		for protocol in protocols:
			p.add_protocol(protocol) 
		p.serialize()
		return p.data

    '''
    Create arp reply
    '''
    def _create_arp_reply(self, arp_packet, dst_mac, eth):
        #dst_mac = answer.
        eth.src = dst_mac
        eth.dst = arp_packet.src_mac
        #eth = ethernet.ethernet(arp_packet.src_mac, dst_mac,ether.ETH_TYPE_ARP)
 		#reverse the src_ip and dst_ip of incomming arp_packet.
 		#src_mac = answer.
        arp_packet.hwtype = arp.ARP_REPLY
        arp_packet.opcode = arp.ARP_REPLY
        arp_packet.dst_mac = arp_packet.src_mac
        arp_packet.src_mac = dst_mac
        tmp_src_ip =  arp_packet.src_ip
        arp_packet.src_ip = arp_packet.dst_ip
        arp_packet.dst_ip = tmp_src_ip
        data = self._generate_packet([eth,arp_packet])
        return data
    
    def _arp_reply(self, datapath, arp_packet, eth):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        target_net_int = None

    	if arp_packet.dst_ip == self.ovs_net_d.ip: # who has "192.168.4.101" 
               target_net_int =  self.ovs_net_d
    	elif arp_packet.dst_ip == self.ovs_net_cloud.ip: #who has "192.168.10.128"
               target_net_int =  self.ovs_net_cloud
        elif arp_packet.dst_ip == self.ovs_net_server.ip: #who has "192.168.8.101"
               target_net_int =  self.ovs_net_server
        else:
           #print "SOMETHING WRONG ARP"
        	return;


        print ("--- PacketIn: ARP_Request: from %s to %s src_mac=%s answer = %s",
               arp_packet.src_ip, arp_packet.dst_ip, arp_packet.src_mac, target_net_int.mac)
        data = self._create_arp_reply( arp_packet, target_net_int.mac, eth)

        buffer_id = 0xffffffff
        in_port = ofproto.OFPP_LOCAL
        actions = [parser.OFPActionOutput(target_net_int.port, 0)]
        msg = parser.OFPPacketOut(datapath, buffer_id, in_port, actions, data)
        datapath.send_msg(msg)
		
    def _swap_ip(self, ip_packet):
    	tmp_src = ip_packet.src
        ip_packet.src = ip_packet.dst
        ip_packet.dst = tmp_src

    def _swap_port(self, udp_packet):
        tmp_src_port = udp_packet.src_port
        udp_packet.src_port = udp_packet.dst_port
        udp_packet.dst_port = tmp_src_port
    
    def _swap_mac(self, eth_packet):
        tmp_src_mac = eth_packet.src
        eth_packet.src = eth_packet.dst
        eth_packet.dst = tmp_src_mac

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

        '''
        Received arp request, does reply
        '''
        if packet.Packet(msg.data).get_protocol(arp.arp):
            arp_packet = packet.Packet(msg.data).get_protocols(arp.arp)[0]
            self._arp_reply(datapath, arp_packet, eth)

        '''
		Received an IP packet from the offloading server (chekinging by comparing src_ip).
		'''
        if ip_packet and ip_packet[0].src == ol_net_server_ip: ##packets from offloading server.
            print "***********Packet from ols**************"
            print "ip_packet[0].src=%s, ip_packet[0].dst=%s"%(ip_packet[0].src,ip_packet[0].dst)
            '''
            Inner IP packet
            '''
            #eth header.
            inner_icmp_packet = packet.Packet(msg.data).get_protocol(icmp.icmp)
            #ip header.
            inner_ipv4 = self.uplink_inner_ipv4
            self._swap_ip(inner_ipv4) #swap IP src/dst of the inner ipv4 header.
            #create the inner icmp packet
            #data = self._create_icmp(eth, inner_ipv4, icmp_packet)
            print inner_ipv4

            '''
            Outer ipv4 header
            '''
            #outer_ipv4 = self.uplink_ipv4
            self._swap_ip(outer_ipv4)	#swap IP srs/dest of the outer ipv4 header
            #outer_ipv4.src = sgw_net_d_ip #disguish OVS's IP by SGW's IP
            #outer_ipv4.dst = enodeb_net_d_ip #disguish OVS's IP by SGW's IP
            print outer_ipv4
            #Outer UDP
            outer_udp_packet = self.uplink_udp
            #self._swap_port(outer_udp_packet)	#swap udp ports
            #outer_udp_packet.src_port = 49407 #trick
            print outer_udp_packet

            '''
            Outer GTP-U header
            '''
            outer_gtp = self.uplink_gtp_header
            outer_gtp.teid = ENODEB_TEID #explicitly set gtp header teid to ENODEB teid.
            print outer_gtp
            '''
            Outer ethernet header
            '''
            outer_eth = self.uplink_eth
            #outer_eth.src = sgw_net_d_mac
            #outer_eth.dst = enodeb_net_d_mac
            #outer_eth = ethernet.ethernet (enodeb_net_d_mac, sgw_net_d_mac, ether.ETH_TYPE_IP)
            self._swap_mac(outer_eth)	#swap ethernet macs
            print outer_eth
            '''
            Whole GTP packet
            '''
            data = self._generate_packet([outer_eth,outer_ipv4,outer_udp_packet,outer_gtp,inner_ipv4,inner_icmp_packet])


            #out port is the port to eNodeB.
            out_port = 2
            #send packet out to port
            actions = [parser.OFPActionOutput(out_port)]
            out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port, actions=actions, data=data)
            datapath.send_msg(out)

            print "##### END GTP #########"
            return
        
        '''
		If received an GTP packet.
		'''
        if packet.Packet(msg.data).get_protocol(udp.udp): #if udp packet
            udp_packet = packet.Packet(msg.data).get_protocols(udp.udp) 
            if udp_packet[0].dst_port == GTP_PORT:
                print "####GTP packet:"
                protocols = pkt.protocols
                #for p in protocols:
                    #proto = packet.Packet(msg.data).get_protocol(p)
                    #print proto.protocol_name

                print "ip_packet[1].src=%s, ip_packet[1].dst=%s"%(ip_packet[1].src,ip_packet[1].dst)
                print "packet in: in_port=%d eth.dst = %s  eth.src = %s  dpid = %d  outport = %d" % (in_port,str(dst),str(src),dpid,out_port)
                print "udp.src_port=%s, udp.dst_port=%s"%(udp_packet[0].src_port,udp_packet[0].dst_port)

                #store uplink outer headers
                self.uplink_gtp_header = packet.Packet(msg.data).get_protocols(gtp.gtp)[0]
                self.uplink_udp = packet.Packet(msg.data).get_protocols(udp.udp)[0]
                self.uplink_ipv4 = packet.Packet(msg.data).get_protocols(ipv4.ipv4)[0]
                self.uplink_eth = packet.Packet(msg.data).get_protocols(ethernet.ethernet)[0]
                self.uplink_inner_ipv4 = packet.Packet(msg.data).get_protocols(ipv4.ipv4)[1]

                print "Gtp.flag=%s, .msg_type=%s, .total_length=%s, .teid=%s" % (str(self.uplink_gtp_header.flag),
                 str(self.uplink_gtp_header.msg_type),
                 str(self.uplink_gtp_header.total_length), 
                 str (self.uplink_gtp_header.teid))

                '''
                Specifically handle icmp packets
                '''
                if packet.Packet(msg.data).get_protocol(icmp.icmp):
                    icmp_packet = packet.Packet(msg.data).get_protocol(icmp.icmp)
                    if ip_packet[1]:
                        '''
                        ICMP packet from ovs to offloading server.
                        '''
                        #eth header.
                        eth.src = ovs_net_server_mac
                        eth.dst = ol_net_server_mac 
                        #ip header.
                        ip_packet[1].src = ovs_net_server_ip #change IP src/dst adds to ovs/ols.
                        ip_packet[1].dst = ol_net_server_ip
                        #create an icmp packet
                        data = self._create_icmp(eth, ip_packet[1], icmp_packet) 
                        #out port is the port to ols.
                        out_port = 3
                        #send icmp out to port 3
                        actions = [parser.OFPActionOutput(out_port)]
                        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port, actions=actions, data=data)
                        datapath.send_msg(out)
                        print "*****To offloading..."
                        print "#####End GTP packet"
                        return

        actions = [parser.OFPActionOutput(out_port)]
		# install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
            self.add_flow(datapath, 1, match, actions)
	    '''
	    Broadcasting arp requests otherwise
	    '''
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)


