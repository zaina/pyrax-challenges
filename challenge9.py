#!/usr/bin/env python
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" Write an application that when passed the arguments FQDN, image, and 
flavor it creates a server of the specified image and flavor with the 
same name as the fqdn, and creates a DNS entry for the fqdn pointing to 
the server's public IP """

import pyrax
import os
import time
import argparse
import re
import sys 

def valid_flavor(flavor):
    if flavor not in ['512MB','1GB','2GB','4GB','8GB','15GB','30GB']:
        raise argparse.ArgumentTypeError("Not a valid flavor [512MB,\
                 1GB, 2GB, 4GB, 8GB, 15GB, 30GB]")
    else: 
        flavor = int(flavor[0:len(flavor)-2:])
        if flavor == 512:
            return flavor
        else:
            return flavor*1024


def valid_fqdn(fqdn):
    msg = "%s is not a valid FQDN" %fqdn
    if len(fqdn) > 255:
        raise argparse.ArgumentTypeError(msg)
    if fqdn[-1:] == ".":
        fqdn = fqdn[:-1] 
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    if all(allowed.match(x) for x in fqdn.split(".")):
        return fqdn
    else:
        raise argparse.ArgumentTypeError(msg)


parser = argparse.ArgumentParser(description='This script creates a cloud server')
parser.add_argument('fqdn', metavar='FQDN', type=valid_fqdn, nargs='+',
                   help='Server FQDN')
parser.add_argument('image', metavar='ImageName', type=str, nargs='+',
                   help='Image Name [Ubuntu, CentOS, Fedora etc...]')
parser.add_argument('flavor', metavar='FlavorName', type=valid_flavor, nargs='+',
                   help='Flavor [512MB, 1GB, 2GB, 4GB, 8GB, 15GB, 30GB]')

args = parser.parse_args()
fqdn = args.fqdn[0]
image = args.image[0]
size = args.flavor[0]

path = os.path.expanduser("~/.rackspace_cloud_credentials")
try:
    pyrax.set_credential_file(path)
except pyrax.exceptions.AuthenticationFailed:
    print "Anthentication failed. Valid credentials needed in", path

cs = pyrax.cloudservers

image = [img for img in cs.images.list() if image in img.name][0]
flavor = [flavor for flavor in cs.flavors.list() if flavor.ram == size][0]

print "Image:", image.name
print "Flavor:", flavor.name

print "Creating Cloud server %s..." % fqdn
server = cs.servers.create(fqdn, image.id, flavor.id)

print "Waiting for networking information..." 
while not server.networks:
    server.get()
    time.sleep(1)
else:
    print "Server %s Created..." %server.human_id
    print "Server Status:", server.status
    print "Root Password:", server.adminPass
    print "Public IP Address:", server.networks["public"] 
    print

print "Creating A record..." 
a_record = {"type": "A",
        "name": fqdn,
        "data": server.networks["public"][0],
        "ttl": 300}

dns = pyrax.cloud_dns
domain  = '.'.join(fqdn.split('.')[-2:])

try:
    zone = dns.find(name=domain)
    zone.add_records(a_record)
    print "DNS record added successfully"
except pyrax.exceptions.NotFound:
    print "Error: Zone '%s' not found" %domain
except pyrax.exceptions.BadRequest as e:
    print "A record creation failed: Bad Request %s" %e
except pyrax.exceptions.DomainRecordAdditionFailed as e:
    print "A record creation failed: %s" %e
