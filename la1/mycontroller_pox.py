# Copyright 2012 James McCauley
#
# This file is part of POX.
#
# POX is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# POX is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with POX.  If not, see <http://www.gnu.org/licenses/>.

"""
This component is for use with the OpenFlow tutorial.

It acts as a simple hub, but can be modified to act like an L2
learning switch.

It's quite similar to the one for NOX.  Credit where credit due. :)
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of
import pox.lib.packet as pkt
from pox.lib.addresses import IPAddr


log = core.getLogger()



class Tutorial (object):
  """
  A Tutorial object is created for each switch that connects.
  A Connection object for that switch is passed to the __init__ function.
  """
  def __init__ (self, connection):
    # Keep track of the connection to the switch so that we can
    # send it messages!
    self.connection = connection

    # This binds our PacketIn event listener
    connection.addListeners(self)

    # Use this table to keep track of which ethernet address is on
    # which switch port (keys are MACs, values are ports).
    self.mac_to_port = {}


  def send_packet (self, buffer_id, raw_data, out_port, in_port):
    """
    Sends a packet out of the specified switch port.
    If buffer_id is a valid buffer on the switch, use that.  Otherwise,
    send the raw data in raw_data.
    The "in_port" is the port number that packet arrived on.  Use
    OFPP_NONE if you're generating this packet.
    """
    msg = of.ofp_packet_out()
    msg.in_port = in_port
    if buffer_id != -1 and buffer_id is not None:
      # We got a buffer ID from the switch; use that
      msg.buffer_id = buffer_id
    else:
      # No buffer ID from switch -- we got the raw data
      if raw_data is None:
        # No raw_data specified -- nothing to send!
        return
      msg.data = raw_data

    # Add an action to send to the specified port
    action = of.ofp_action_output(port = out_port)
    msg.actions.append(action)

    # Send message to switch
    self.connection.send(msg)


  def act_like_hub (self, packet, packet_in):
    """
    Implement hub-like behavior -- send all packets to all ports besides
    the input port.
    """

    # We want to output to all ports -- we do that using the special
    # OFPP_FLOOD port as the output port.  (We could have also used
    # OFPP_ALL.)
    #self.send_packet(packet_in.buffer_id, packet_in.data,
    #                 of.OFPP_FLOOD, packet_in.in_port)

    # Note that if we didn't get a valid buffer_id, a slightly better
    # implementation would check that we got the full data before
    # sending it (len(packet_in.data) should be == packet_in.total_len)).


  def parseIP (self, packet):
	print "Controller received pkt.type %s \n" % packet.type
	ip_packet = packet
	if packet.type == 0x8080:
		ip_packet = packet.payload
	return ip_packet

  def act_like_switch (self, packet, packet_in):


    # Here's some psuedocode to start you off implementing a learning
    # switch.  You'll need to rewrite it as real Python code.

    # Learn the port for the source MAC
    #self.mac_to_port ... <add or update entry>

    #if the port associated with the destination MAC of the packet is known:
      # Send packet out the associated port
    #  self.send_packet(packet_in.buffer_id, packet_in.data,
    #                   ..., packet_in.in_port)

      # Once you have the above working, try pushing a flow entry
      # instead of resending the packet (comment out the above and
      # uncomment and complete the below.)

    #  log.debug("Installing flow...")
      # Maybe the log statement should have source/destination/port?
  
      #match = of.ofp_match(in_port = 1, nw_src = "10.0.0.1", nw_dst = "10.0.0.100")
      ## Set fields to match received packet
      #ip_packet = self.parseIP(packet)
      print "Controller received pkt.type %s \n" % packet.type
      ip_packet = packet.find('ipv4')
      if ip_packet is None:
	print "Not IP pkt, return ...\n"
	#return
      #if ip_packet.srcip == "10.0.0.1" and ip_packet.dstip == "10.0.0.100":

      #pkts to 10.0.10.0/24 will be:
	#1. Rewritten its destination IP to rIP 10.0.0.2
	#2. Forwarded to port 2.
      msg = of.ofp_flow_mod()
      msg.match.dl_type = 0x800	#ip packet
      msg.match.nw_dst = "10.0.10.0/24"	#host 2 rIP
      msg.actions.append(of.ofp_action_nw_addr.set_dst(IPAddr("10.0.0.2")))	#set pkt's dst IP to h2 rIP.
      msg.actions.append(of.ofp_action_output(port=2))
      self.connection.send(msg)

	#pkts to 10.0.0.0/24 (reversed path) will be:
	#1. Rewritten its destination IP to rIP 10.0.0.2
	#2. Forwarded to port 2.
      msg = of.ofp_flow_mod()
      msg.match.dl_type = 0x800	#ip packet
      msg.match.nw_dst = "10.0.0.0/24"	# 2 rIP
      msg.actions.append(of.ofp_action_nw_addr.set_src(IPAddr("10.0.10.1")))	#set src IP to vIP.
      msg.actions.append(of.ofp_action_output(port=1))
      self.connection.send(msg)

      #< Set other fields of flow_mod (timeouts? buffer_id?) >
      #
      #< Add an output action, and send -- similar to send_packet() >

    #else
      # Flood the packet out everything but the input port
      # This part looks familiar, right?
      #self.send_packet(packet_in.buffer_id, packet_in.data,
      #                 of.OFPP_FLOOD, packet_in.in_port)



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
    Tutorial(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)
