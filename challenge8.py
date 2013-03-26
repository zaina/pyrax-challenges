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

""" This script creates a cdn enabled container that serves an index 
	file and creates a CNAME record pointing to the CDN URL 
	of the container""" 

import pyrax
import os
import time
import sys
import argparse

parser = argparse.ArgumentParser(description='This script creates a CDN enabled container in Cloud Files')
parser.add_argument('container', metavar='ContainerName', type=str, nargs='+', 
				help='Name of the Cloud Files container, if it \
					doesn\'t exist it will be created.')
args = parser.parse_args()

container_name = args.container[0]

credentials_file = os.path.expanduser("~/.rackspace_cloud_credentials")
try:
	pyrax.set_credential_file(credentials_file)
except pyrax.exceptions.AuthenticationFailed:
	print "Anthentication failed. Valid credentials needed in ~/.rackspace_cloud_credentials"

cf = pyrax.cloudfiles

print "Creating container if it doesn't exist..."
cont = cf.create_container(container_name)
print "Making container public..."
cont.make_public(ttl=300)
print "Container Name:", cont.name
print "CDN Enabled:", cont.cdn_enabled
print "TTL:", cont.cdn_ttl

text = "<h1>Hello World!</h1>"
"""with pyrax.utils.SelfDeletingTempfile() as index_file:
	with file(index_file, "w") as tmp:
		tmp.write(text)
	path = os.path.basename(index_file)
	print "Uploading file: %s" % path
	cf.upload_file(cont, index_file, content_type="text/text")
"""
chksum = pyrax.utils.get_checksum(text)
index_file = cf.store_object(cont, "index.html", text)
print "Calculated checksum:", chksum
print "Stored object etag:", index_file.etag

print "Container CDN URI", cont.cdn_uri
#TODO
