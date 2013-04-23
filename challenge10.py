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

''' Write an application that will:
- Create 2 servers, supplying a ssh key to be installed at 
 /root/.ssh/authorized_keys.
- Create a load balancer
- Add the 2 new servers to the LB
- Set up LB monitor and custom error page. 
- Create a DNS record based on a FQDN for the LB VIP. 
- Write the error page html to a file in cloud files for backup. '''

import pyrax
import os
import time
import argparse
import re
import sys 

# Number of servers to build
limit = 2
prefix = "zzz"

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
                   help='FQDN for the Load Balancer VIP')
parser.add_argument('image', metavar='ImageName', type=str, nargs='+',
                   help='Image Name [Ubuntu, CentOS, Fedora etc...]')
parser.add_argument('flavor', metavar='FlavorName', type=valid_flavor, nargs='+',
                   help='Flavor [512MB, 1GB, 2GB, 4GB, 8GB, 15GB, 30GB]')
parser.add_argument('key', metavar='SSHKey', type=argparse.FileType('r'), nargs='+',
                   help='Path to the Public SSH key file')

args = parser.parse_args()
fqdn = args.fqdn[0]
image = args.image[0]
size = args.flavor[0]
key = args.key[0]

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

files = {"/root/.ssh/authorized_keys": key.read()}

print "Creating %s Cloud servers..." %limit


servers = []
for i in range(limit):
    name = prefix + str(i)
    server = cs.servers.create(name, image.id, flavor.id, files=files)
    servers.append(server)

clb = pyrax.cloud_loadbalancers
nodes = []

print "Waiting for networking information..." 
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
            node = clb.Node(address=server.networks["private"][0], port=80, condition="ENABLED")
            nodes.append(node)
            servers.remove(server)


# Create the LB Virtual IP
vip = clb.VirtualIP(type="PUBLIC")

lb = clb.create(fqdn, port=80, protocol="HTTP", nodes=nodes, virtual_ips=[vip])

print "Load Balancer:", lb.name
print "ID:", lb.id
print "Status:", lb.status
print "Nodes:", lb.nodes
print "Virtual IPs:", lb.virtual_ips
print "Algorithm:", lb.algorithm
print "Protocol:", lb.protocol
print

print "Creating A record for the Load Balancer..." 
a_record = {"type": "A",
        "name": fqdn,
        "data": lb.virtual_ips[0].address,
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

# Waiting for LB to become ACTIVE
print "Waiting for LB to become ACTIVE..."
while not "ACTIVE" in clb.get(lb).status:
    time.sleep(1)

# Adding custom error page
html = "<html><body>Oops, something is broken!</body></html>"
lb.set_error_page(html)
print
print "Custom Error Page added"

# Storing custom error page in Cloud Files
cf = pyrax.cloudfiles
container = cf.create_container("custom_error_pages")

obj = cf.store_object(container, "error.html", html)
print "Custom Error Page stored in CF", obj

# Adding a TCP Connection Health Monitor
#lb.add_health_monitor(type="CONNECT", delay=10, timeout=10, attemptsBeforeDeactivation=3)


