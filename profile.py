
# The profile for experimenting with QUIC protocol  
# Updated for a 6-node topology with 2 link bridges. Python 2 compatible.

import geni.portal as portal
import geni.rspec.pg as pg
import geni.rspec.emulab as emulab

pc = portal.Context()
request = pc.makeRequestRSpec()

pc.defineParameter("quic_version", "Specify the quic version to setup (Q037, RFCv1)", portal.ParameterType.STRING, "RFCv1")
pc.defineParameter("project", "Specify the emulab project name", portal.ParameterType.STRING, "FEC-HTTP")

params = pc.bindParameters()
valid_versions = ["Q037", "RFCv1"]
if params.quic_version not in valid_versions:
    pc.reportError(portal.ParameterError("Invalid quic_version. It should be either 'Q037' or 'RFCv1'.", ['quic_version']))
pc.verifyParameters()

ubuntu_22 = "urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU22-64-STD"
ubuntu_18 = "urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU18-64-STD"
fbsd_image = "urn:publicid:IDN+emulab.net+image+emulab-ops:FBSD132-64-STD"
ubuntu_image = ubuntu_22 if params.quic_version == 'RFCv1' else ubuntu_18

# SERVER 1
server1 = request.RawPC("server1")
server1.hardware_type = "d430"
server1.disk_image = ubuntu_image
s1_iface = server1.addInterface("s1_iface")
s1_iface.addAddress(pg.IPv4Address("192.168.1.1", "255.255.255.0"))

# SERVER 2
server2 = request.RawPC("server2")
server2.hardware_type = "d430"
server2.disk_image = ubuntu_image
s2_iface = server2.addInterface("s2_iface")
s2_iface.addAddress(pg.IPv4Address("192.168.1.2", "255.255.255.0"))

# CLIENT 1
client1 = request.RawPC("client1")
client1.hardware_type = "d710"
client1.disk_image = ubuntu_image
c1_iface = client1.addInterface("c1_iface")
c1_iface.addAddress(pg.IPv4Address("192.168.2.1", "255.255.255.0"))

# CLIENT 2
client2 = request.RawPC("client2")
client2.hardware_type = "d710"
client2.disk_image = ubuntu_image
c2_iface = client2.addInterface("c2_iface")
c2_iface.addAddress(pg.IPv4Address("192.168.2.2", "255.255.255.0"))

# LINK BRIDGE 1
bridge1 = request.RawPC("bridge1")
bridge1.hardware_type = "d710"
bridge1.disk_image = fbsd_image
b1_s1 = bridge1.addInterface("b1_s1")
b1_s2 = bridge1.addInterface("b1_s2")
b1_core = bridge1.addInterface("b1_core")

# LINK BRIDGE 2
bridge2 = request.RawPC("bridge2")
bridge2.hardware_type = "d710"
bridge2.disk_image = fbsd_image
b2_c1 = bridge2.addInterface("b2_c1")
b2_c2 = bridge2.addInterface("b2_c2")
b2_core = bridge2.addInterface("b2_core")

# Connections
link_s1 = request.Link("link_s1")
link_s1.addInterface(s1_iface)
link_s1.addInterface(b1_s1)

link_s2 = request.Link("link_s2")
link_s2.addInterface(s2_iface)
link_s2.addInterface(b1_s2)

link_c1 = request.Link("link_c1")
link_c1.addInterface(c1_iface)
link_c1.addInterface(b2_c1)

link_c2 = request.Link("link_c2")
link_c2.addInterface(c2_iface)
link_c2.addInterface(b2_c2)

link_core = request.Link("link_core")
link_core.addInterface(b1_core)
link_core.addInterface(b2_core)

project = params.project
for node in [server1, server2, client1, client2]:
    node.addService(pg.Execute(shell="sh", command="export PROJECT={} QUIC_VERSION={} && /local/repository/scripts/install-deps.sh".format(project, params.quic_version)))

server1.addService(pg.Execute(shell="sh", command="/local/repository/scripts/install-apache.sh"))
server2.addService(pg.Execute(shell="sh", command="/local/repository/scripts/install-apache.sh"))

client1.addService(pg.Execute(shell="sh", command="export QUIC_VERSION={} && /local/repository/scripts/install-client.sh".format(params.quic_version)))
client2.addService(pg.Execute(shell="sh", command="export QUIC_VERSION={} && /local/repository/scripts/install-client.sh".format(params.quic_version)))

bridge1.addService(pg.Execute(shell="sh", command="/local/repository/scripts/bridge-tunning.sh"))
bridge2.addService(pg.Execute(shell="sh", command="/local/repository/scripts/bridge-tunning.sh"))

pc.printRequestRSpec(request)
