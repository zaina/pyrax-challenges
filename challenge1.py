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

""" This script builds three 512MB CentOS Servers and returns the 
	IP and login credentials for each one."""

# Script variables
limit = 3
size = 512
image = "CentOS"
servername = "server"

import pyrax
import os
import time

credentials_file = os.path.expanduser("~/.rackspace_cloud_credentials")
try:
	pyrax.set_credential_file(credentials_file)
except pyrax.exceptions.AuthenticationFailed:
	print "Anthentication failed. Valid credentials needed in ~/.rackspace_cloud_credentials"

cs = pyrax.cloudservers
flavor = [flavor for flavor in cs.flavors.list() if flavor.ram == size][0]
image = [img for img in cs.images.list() if image in img.name][0]

print "Building %s %s %s servers." %(limit,size,image.name)
print

servers = []
print "Starting server builds..."
for i in range(0,limit):
	server_name = servername + str(i+1)
	server = cs.servers.create(server_name, image.id, flavor.id)
	servers.append(server) 

#print servers

print "Wait for networking to be provisioned..."
print
while servers:
	for server in servers:
		if not server.networks:
			server.get()
			time.sleep(1)
		else:
			print "Server %s Created..." %server.human_id
			print "Server Status:", server.status
			print "Root Password:", server.adminPass
			print "Public IP Address:", server.networks["public"]
			print	
			servers.remove(server)
