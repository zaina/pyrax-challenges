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

""" This script clones a cloud server, takes the server's UUID 
	as only input """

import pyrax
import os
import time
import sys

server_id = raw_input("Please enter the ID of the server that you would like to clone: ")

#print "Using credentials file"
credentials_file = os.path.expanduser("~/.rackspace_cloud_credentials")
try:
	pyrax.set_credential_file(credentials_file)
except pyrax.exceptions.AuthenticationFailed:
	print "Anthentication failed. Valid credentials needed in ~/.rackspace_cloud_credentials"
#print "authenticated =", pyrax.identity.authenticated
#print

cs = pyrax.cloudservers

try:
	server = cs.servers.get(server_id)
	print "Server found!"
except pyrax.exceptions.ServerNotFound:
	print "Server with ID %s was not found" % server_id
	sys.exit(1)
print "Creating a snapshot image of server %s..." % server.human_id
image_name = server.human_id + "_clone"
image_id = server.create_image(image_name)

while "ACTIVE" not in cs.images.get(image_id).status:
  time.sleep(1)

#print image_id
#print dir(server)

#sys.exit(0)
print "Building a new server from the image %s..." % image_name
server_clone = cs.servers.create(image_name, image_id, server.flavor['id'])
print "Root Password: %s" % server_clone.adminPass
print "Server Status: %s" % server_clone.status
print "Server Name: %s" % server_clone.human_id
print "Server ID: %s" % server_clone.id

while not cs.servers.get(server_clone.id).networks:
  time.sleep(1)
print "Public IP Address: %s" % cs.servers.get(server_clone.id).networks["public"]
