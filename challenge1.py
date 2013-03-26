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

import pyrax
import os
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
flavor_512 = [flavor for flavor in cs.flavors.list() if flavor.ram == 512][0]
cent_img = [img for img in cs.images.list() if "CentOS" in img.name][0]

server_names = ["zen1","zen2","zen3"]
for name in server_names:
	print "Creating server %s..." %name
	server = cs.servers.create(name, cent_img.id, flavor_512.id)
	print "Root Password: %s" % server.adminPass
	# Wait for networking to be provisioned
	while not cs.servers.get(server.id).networks:
		time.sleep(1)
	network = cs.servers.get(server.id).networks
	print "Public IP Address: %s" % network["public"]
	print "Private IP Address: %s" % network["private"]
	print

