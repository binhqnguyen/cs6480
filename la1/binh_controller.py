 




                if packet.payload.protocol == ipv4.ICMP_PROTOCOL:
                        ##do nothing. Just leave the ICMP message to follow the flow-table.
                        log.debug("received a ICMP proto mesage\n")


import random
from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr
from pox.lib.addresses import EthAddr
import pox.lib.packet as pkt
from pox.lib.packet.ethernet import ethernet
from pox.lib.packet.ipv4 import ipv4
from pox.lib.packet.arp import arp
from pox.lib.packet.dns import dns

log = core.getLogger()

class Tutorial (object):

    def __init__ (self, connection):
        # Keep track of the connection to the switch so that we can
        # send it messages!
        self.connection = connection

        # This binds our PacketIn event listener
        connection.addListeners(self)

        # Use this table to keep track of which ethernet address is on
        # which switch port (keys are MACs, values are ports).
        self.mac_to_port = {}

        #rIP-vIP mapping
        self.rIP_vIP = {}

        self.rIP_MAC = {}
        #MAC address to port number mapping on switch
        self.MAC_port = {}
        #DNS server IP address.
        self.DNS_SERVER_IP = IPAddr("10.0.0.10")
        #Protected host
        self.PROTECTED_HOST_IP = IPAddr("10.0.0.3")
        #Default port of protected host.
        self.default_outport = 3
        #record used vIPs to avoid vIP reuse
        self.used_vIP = []
        #self.add_vflow(sIP,vIP,rIP)
        #Register some dns records manually.
        self.register_dns_records()
        #Register rIP to MAC mapping manually.
        self.register_IP_mac_mapping()


    def DNS_respond(self, packet, packet_in):
        def create_vIP(rIP):
                random.seed()
                while True: #iterate until a "good" vIP found
                        A = 10
                        B = random.randint(0,254)
                        C = random.randint(1,254)
                        D = random.randint(1,254)
                        vIP = IPAddr(str (str(A)+"."+str(B)+"."+str(C)+"."+str(D)))
                        if vIP not in self.used_vIP:
                                #map the rIP to the vIP
                                self.rIP_vIP[rIP] = vIP
                                #register used vIP
                                self.used_vIP.append(vIP)
                                log.debug("random vIP created, <vIP, rIP> =  <%s,%s>\n" % (vIP,rIP))
                                break

        def push_flow(sIP,vIP,rIP,in_port,out_port):
                  #pkts to 10.0.10.0/24 will be:
                  #1. Rewritten its destination IP to rIP
                  #2. Forwarded to out_port.
                msg_send = of.ofp_flow_mod()
                msg_send.match.dl_type = 0x800 #ip packet
                msg_send.match.in_port = in_port
                msg_send.match.nw_dst = vIP  #host 2 vIP
                msg_send.actions.append(of.ofp_action_nw_addr.set_dst(IPAddr(rIP)))     #set pkt's dst IP to h
2 rIP.
                msg_send.actions.append(of.ofp_action_output(port=out_port))
                self.connection.send(msg_send)

                  #pkts to 10.0.0.0/24 (reserved path)  will be:
                  #1. Rewritten its src IP to vIP.
                  #2. Forwarded to port 1.
                msg_rep = of.ofp_flow_mod()                                                 
                msg_rep.match.dl_type = 0x800 #ip packet                                    
                msg_rep.match.in_port = out_port                                            
                msg_rep.match.nw_dst = sIP  # h1 rIP                                        
                msg_rep.actions.append(of.ofp_action_nw_addr.set_src(IPAddr(vIP)))    #set src IP to vIP. 
                msg_rep.actions.append(of.ofp_action_output(port=in_port))                  
                self.connection.send(msg_rep)                                               
                                                                                            
        dns_req = packet.find('dns')                                                        
                                                                                            
        if dns_req is not None:                                                             
                questions_answers = {} 
                for q in dns_req.questions:
                        log.debug("Question = %s\n" % q)
                        qs = str(q).split()
                        if qs[0] in self.dns_records:
                                resolved_IP = self.dns_records[qs[0]]
                                log.info("dns record found: %s->%s\n" %(q, resolved_IP))
                                #register resolved answer (rIP) and create a vIP for the rIP
                                create_vIP(resolved_IP)
                                #put the VIRTUAL IP into DNS answer
                                questions_answers[q] = self.rIP_vIP[resolved_IP]
                                log.debug("%s,%s" % (q, questions_answers[q]))

                if len(questions_answers) > 0:
                        dns_rep = self.create_dns_rep(dns_req,questions_answers)
                        ipv4_dns_rep = self.create_ipv4_dns(packet, dns_rep)
                        self.send_packet(ipv4_dns_rep.pack(), packet_in.in_port)
                        push_flow(packet.payload.srcip, self.rIP_vIP[resolved_IP], resolved_IP,packet_in.in_po
rt,self.default_outport)
                        log.info("Flow pushed srcip,vIP,rIP,in_port,out_port = %s, %s, %s,%s,%s\n" % (packet.p
ayload.srcip, self.rIP_vIP[resolved_IP], resolved_IP, packet_in.in_port, self.default_outport))
                else: log.info("no dns found\n" )






    def respond_to_arp(self, packet, packet_in):

        def create_arp_respond(arp_req, answer):
                arp_rep = pkt.arp()
                arp_rep.opcode = arp_req.payload.REPLY
                arp_rep.hwdst = arp_req.src
                arp_rep.protodst = arp_req.payload.protosrc
                arp_rep.protosrc = arp_req.payload.protodst
                arp_rep.hwsrc = answer
                return arp_rep

        def create_eth_packet(src, dst, payload):
                ether = ethernet()
                ether.type = pkt.ethernet.ARP_TYPE
                ether.dst = dst
                ether.src = src
                ether.payload = payload
                return ether
        def vIP_to_rIP(s_vIP):
                for rIP,vIP in self.rIP_vIP.iteritems():
                        log.debug("vIP->rIP: %s->%s"%(vIP,rIP))
                        if s_vIP == vIP:
                                return rIP

        ask_for_vIP = packet.payload.protodst
        ask_for_rIP = vIP_to_rIP(ask_for_vIP)
        log.debug("ARP asking for vIP=%s (rIP=%s)"%(ask_for_vIP,ask_for_rIP) )
        if ask_for_rIP in self.mac_mapping:
                answer = EthAddr(self.mac_mapping[ask_for_rIP])
                log.debug("responding to ARP request to reach %s (ACTUALLY rIP %s), answer is %s\n" % (ask_for
_vIP,ask_for_rIP, str(answer)))
                arp_rep = create_arp_respond(packet, answer)
                ether = create_eth_packet(arp_rep.hwsrc, packet.src, arp_rep)
                self.send_packet(ether.pack(),packet_in.in_port)
        else:   log.info("No MAC found with requested ip %s\n" % ask_for_rIP)

  def register_dns_records(self):
        self.dns_records = {}
        log.debug("Registering hostname-ip dns records...\n")
        self.dns_records["target"] = self.PROTECTED_HOST_IP

  def register_IP_mac_mapping(self):
        self.mac_mapping = {}
        log.debug("Registering rIP-MAC mapping, fixed vIP-rIP, and used vIP...\n")
        for i in range (1,11):
                self.mac_mapping[IPAddr("10.0.0."+str(i))] = EthAddr("00:00:00:00:00:0"+str(i))
                self.rIP_vIP[IPAddr("10.0.0."+str(i))] = IPAddr("10.0.0."+str(i))
                self.used_vIP.append(IPAddr("10.0.0."+str(i)))
        #register MAC-port mapping
        self.MAC_port[EthAddr("00:00:00:00:00:0"+str(i))] = i

  def create_dns_rep(self, dns_req, questions_answers):
        dns_rep = pkt.dns()
        dns_rep.questions = dns_req.questions
        answers = []
        log.debug(questions_answers)
        for q in questions_answers.keys():
                #log.debug("q = %s" % q)
                #log.debug ("<question,answer>=<%s,%s>.\n") % (str(q), questions_answers[q]) 
                answers.append(pkt.dns.rr(str(q).split()[0],
                                          pkt.dns.rr.A_TYPE,
                                          1, 1,
                                          len(questions_answers[q].toRaw()),questions_answers[q]))
        dns_rep.answers = answers
        dns_rep.authorities = dns_req.authorities
        dns_rep.id = dns_req.id
        dns_rep.opcode = dns_req.opcode
        dns_rep.aa = True
        dns_rep.qr = True
        #TODO: more dns fields.
        return dns_rep

    def create_ipv4_dns(self, req_packet,  dns_rep):
        ether_req = req_packet.find('ethernet')
        udp_req = req_packet.find('udp')
        ipv4_req = req_packet.find('ipv4')
        if ether_req is None or udp_req is None or ipv4_req is None:
                return
        ether_rep = pkt.ethernet(ether_req.raw) #reply ethernet
        udp_rep = pkt.udp(udp_req.raw)  #reply upd pkt
        ipv4_rep = pkt.ipv4(ipv4_req.raw)       #reply ipv4 pkt
        #swap MACs
        ether_rep.dst = ether_req.src
        ether_rep.src = ether_req.dst
        ether_rep.type = pkt.ethernet.IP_TYPE
        #swap udp ports.
        udp_rep.dstport = udp_req.srcport
        udp_rep.srcport = 53
        #swap ipaddresses.
        ipv4_rep.srcip = ipv4_req.dstip
        ipv4_rep.dstip = ipv4_req.srcip
        #ipv4_rep.srcport = ipv4_req.dstport
        #ipv4_rep.dstport = ipv4_req.srcport
        #put payloads
        udp_rep.payload = dns_rep
        ipv4_rep.payload = udp_rep
        ether_rep.payload = ipv4_rep
        return ether_rep
        

  ##Send an ethernet packet to outport
  #packet_in: ethernet.pack()
  #out_port: output port        
  def send_packet (self, packet_in, out_port):
    msg = of.ofp_packet_out()
    msg.data = packet_in

    # Add an action to send to the specified port
    action = of.ofp_action_output(port = out_port)
    msg.actions.append(action)

    # Send message to switch
    self.connection.send(msg)

  def _handle_PacketIn (self, event):
    """
    Handles packet in messages from the switch.
    """

    packet = event.parsed # This is the parsed packet data.
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return

    packet_in = event.ofp # The actual ofp_packet_in message.

    # Comment out the following line and uncomment the one after
    # when starting the exercise.
    #self.act_like_hub(packet, packet_in)
    self.act_like_switch(packet, packet_in)

def launch ():
  """
  Starts the component
  """
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    Binh_Controller(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)



                                                                                            299,3         Bot
                                resolved_IP = self.dns_records[qs[0]]
                                log.info("dns record found: %s->%s\n" %(q, resolved_IP))
                                #register resolved answer (rIP) and create a vIP for the rIP
                                create_vIP(resolved_IP)
                                #put the VIRTUAL IP into DNS answer
                                questions_answers[q] = self.rIP_vIP[resolved_IP]
                                log.debug("%s,%s" % (q, questions_answers[q]))

                if len(questions_answers) > 0:
                        dns_rep = self.create_dns_rep(dns_req,questions_answers)
                        ipv4_dns_rep = self.create_ipv4_dns(packet, dns_rep)
                        self.send_packet(ipv4_dns_rep.pack(), packet_in.in_port)
                        push_flow(packet.payload.srcip, self.rIP_vIP[resolved_IP], resolved_IP,packet_in.in_po
rt,self.default_outport)
                        log.info("Flow pushed srcip,vIP,rIP,in_port,out_port = %s, %s, %s,%s,%s\n" % (packet.p
ayload.srcip, self.rIP_vIP[resolved_IP], resolved_IP, packet_in.in_port, self.default_outport))
                else: log.info("no dns found\n" )


  def act_like_switch (self, packet, packet_in):

      if packet.type == packet.ARP_TYPE:
                log.debug("received an ARP pkt\n")
                if packet.payload.opcode == packet.payload.REQUEST: #received an ARP request
                        self.respond_to_arp(packet, packet_in)
      if packet.type == ethernet.IP_TYPE:
                if packet.payload.dstip == self.DNS_SERVER_IP:  #if this is a DNS request
                        log.debug("received a DNS request\n")
                        self.DNS_respond(packet,packet_in)
                if packet.payload.protocol == ipv4.ICMP_PROTOCOL:
                        ##do nothing. Just leave the ICMP message to follow the flow-table.




