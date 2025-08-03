
import geni.portal as portal
import geni.rspec.pg as pg
import geni.rspec.emulab as emulab

pc = portal.Context()
request = pc.makeRequestRSpec()

pc.defineParameter("quic_version", "Specify the quic version to setup (Q037, RFCv1)", portal.ParameterType.STRING, "RFCv1")
pc.defineParameter("project", "Specify the emulab project name", portal.ParameterType.STRING, "FEC-HTTP")

params = pc.bindParameters()
pc.verifyParameters()

# Define basic images
ubuntu_image = "urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU22-64-STD"
fbsd_image = "urn:publicid:IDN+emulab.net+image+emulab-ops:FBSD132-64-STD"

# Setup hosts with IPs
server1 = request.RawPC("server1")
server1.disk_image = ubuntu_image
s1 = server1.addInterface()
s1.addAddress(pg.IPv4Address("192.168.1.1", "255.255.255.0"))

server2 = request.RawPC("server2")
server2.disk_image = ubuntu_image
s2 = server2.addInterface()
s2.addAddress(pg.IPv4Address("192.168.1.2", "255.255.255.0"))

client1 = request.RawPC("client1")
client1.disk_image = ubuntu_image
c1 = client1.addInterface()
c1.addAddress(pg.IPv4Address("192.168.2.1", "255.255.255.0"))

client2 = request.RawPC("client2")
client2.disk_image = ubuntu_image
c2 = client2.addInterface()
c2.addAddress(pg.IPv4Address("192.168.2.2", "255.255.255.0"))

# Setup bridges (no IPs)
bridge1 = request.RawPC("bridge1")
bridge1.disk_image = fbsd_image
b1_1 = bridge1.addInterface()
b1_2 = bridge1.addInterface()
b1_core = bridge1.addInterface()

bridge2 = request.RawPC("bridge2")
bridge2.disk_image = fbsd_image
b2_1 = bridge2.addInterface()
b2_2 = bridge2.addInterface()
b2_core = bridge2.addInterface()

# Create links (mixed IP/no IP still causes issues)
request.Link("link_s1").addInterface(s1).addInterface(b1_1)
request.Link("link_s2").addInterface(s2).addInterface(b1_2)
request.Link("link_c1").addInterface(c1).addInterface(b2_1)
request.Link("link_c2").addInterface(c2).addInterface(b2_2)
request.Link("link_core").addInterface(b1_core).addInterface(b2_core)

pc.printRequestRSpec(request)
