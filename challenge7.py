#!/usr/bin/env python

""""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

""" This script creates 2 sloud servers and adds them to a new CLB"""

import pyrax
import os
import sys
import time

print "Using credentials file"
credentials_file = os.path.expanduser("~/.rackspace_cloud_credentials")
try:
	pyrax.set_credential_file(credentials_file)
except pyrax.exceptions.AuthenticationFailed:
	print "Anthentication failed. Valid credentials needed in ~/.rackspace_cloud_credentials"
print "authenticated =", pyrax.identity.authenticated
print

cs = pyrax.cloudservers
clb = pyrax.cloud_loadbalancers

flavor_512 = [flavor for flavor in cs.flavors.list() if flavor.ram == 512][0]
centos_img = [img for img in cs.images.list() if "CentOS" in img.name][0]
nodes = []
server_names = ["web1","web2"]
for server_name in server_names:
	print "Creating server %s..." %server_name
	server = cs.servers.create(server_name, centos_img.id, flavor_512.id)
	print "Root Password: %s" % server.adminPass
	# Wait for networking to be provisioned
	while not server.networks:
		server.get()
		if "ERROR" in server.status:
			print "Server creation failed. Exiting"
			sys.exit(1)
		time.sleep(1)
	network = cs.servers.get(server.id).networks
	print "Public IP Address: %s" % network["public"]
	print
	node = clb.Node(address=network["private"][0], port=80, condition="ENABLED")
	nodes.append(node)

#print nodes

print "Creating a load Balancer..."
vip = clb.VirtualIP(type="PUBLIC")
lb = clb.create("WebLB", port=80, protocol="HTTP", nodes=nodes, virtual_ips=[vip])

#print "Node:", node.to_dict()
print "Virtual IP:", vip.to_dict()
print "Load Balancer:", lb
