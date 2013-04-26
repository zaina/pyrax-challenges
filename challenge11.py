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
Create an SSL terminated load balancer (Create self-signed certificate.)
Create a DNS record that should be pointed to the load balancer.
Create Three servers as nodes behind the LB.
     Each server should have a CBS volume attached to it. (Size and type are irrelevant.)
     All three servers should have a private Cloud Network shared between them.
     Login information to all three servers returned in a readable format as the result of the script, including connection information.'''

import pyrax
import os
import time
import argparse
import re
import sys 

# Number of servers to build
limit = 3
# Server name prefix
prefix = "zzz"
# SSL cert info
cert = "-----BEGIN CERTIFICATE-----\nMIIDWDCCAkCgAwIBAgIJAIX0ewLet+8+MA0GCSqGSIb3DQEBBQUAMGAxCzAJBgNV\nBAYTAlVTMQ4wDAYDVQQIEwVUZXhhczEUMBIGA1UEBxMLU2FuIGFudG9uaW8xEjAQ\nBgNVBAoTCVJhY2tzcGFjZTEXMBUGA1UEAxMOZnFkbi56YWluYS5jb20wHhcNMTMw\nNDIzMDM1MTU2WhcNMjMwNDIxMDM1MTU2WjBgMQswCQYDVQQGEwJVUzEOMAwGA1UE\nCBMFVGV4YXMxFDASBgNVBAcTC1NhbiBhbnRvbmlvMRIwEAYDVQQKEwlSYWNrc3Bh\nY2UxFzAVBgNVBAMTDmZxZG4uemFpbmEuY29tMIIBIjANBgkqhkiG9w0BAQEFAAOC\nAQ8AMIIBCgKCAQEAs0wYJGYh+fzBVAPEHOGZ3UFAdofRV3T3YkjJv2CkkvM4bf3B\nyiCUPXKjYbACbtcL1Ni3ghwcy86Y9ZAZd6uF0NFsCNXFfqrJ+FnTIjVuvHBuqZwj\nt0UKNDGSpEg4aTp4SlkBRNrjwSH+nq4+bJ0yGv8p4+PAI2XplaT18t6YWbX10Dud\nyB+cpLgX7E1TdoMhIc8u41s6AAYZzNE5mfuvtxYldUFeja3FPuZ4QsCdJ+yLSKVC\ntbW1zLXkFs/Z94FcB8Ra+lGi9nzpnrobeaWUv8iPjhqm/AHHO8M69Ee0Ir4RtcPU\nEQHxaHeNzevh2TiOzMzgI7arsCpdeRrfAhefDwIDAQABoxUwEzARBglghkgBhvhC\nAQEEBAMCBkAwDQYJKoZIhvcNAQEFBQADggEBAKE+ocHtY1aHEEPNqp62/3YH4JA6\n9xYeffFq8tKsIRRYN7OU1tHKOsp+CMOWs3X8ivkved2SmzzAjMMw/03d7THTwCXX\nrqcwyJ4b1KmKB1GD2jX4Ro2LNaIjQ/1r7WuCYuUIKBzAENQ6RaduxXpxxOL3iK6E\n/0UZ7Io3BwIkS632HsSqksRWY++GKG/pWOxdAP+3Hl0rouHorbwJmy0/aAv+XRBv\nWj8cZ4MzRgQjc7h2j7BYMKS7V8+esrMPFOUCOBKBIpiLQw9m2j4cCHCuBAE461yE\nRmek+8x1ekWkoaHgtBpBqkcj0CYJKbPYFkmd3Z6GbzNwyOzCzDyhA+D/Y18=\n-----END CERTIFICATE-----"

key = "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEAs0wYJGYh+fzBVAPEHOGZ3UFAdofRV3T3YkjJv2CkkvM4bf3B\nyiCUPXKjYbACbtcL1Ni3ghwcy86Y9ZAZd6uF0NFsCNXFfqrJ+FnTIjVuvHBuqZwj\nt0UKNDGSpEg4aTp4SlkBRNrjwSH+nq4+bJ0yGv8p4+PAI2XplaT18t6YWbX10Dud\nyB+cpLgX7E1TdoMhIc8u41s6AAYZzNE5mfuvtxYldUFeja3FPuZ4QsCdJ+yLSKVC\ntbW1zLXkFs/Z94FcB8Ra+lGi9nzpnrobeaWUv8iPjhqm/AHHO8M69Ee0Ir4RtcPU\nEQHxaHeNzevh2TiOzMzgI7arsCpdeRrfAhefDwIDAQABAoIBAQCJH+dO3zWZBS+u\nW3r/Q6LzTlZI0LLQGkqgxl5VmUoEgTNlG6+8MJJvNF+z9HLH5nvL+zrNrUZwsL7W\n/7Aaj/m1rJTdZPC4YVI6OCh7fzYDtFFOMnY2Ufzt0gP+1KUgBXG+GrgXuvh42tDq\n9wQS+V46u2+ENMjbybONmS3o40jNQk0CW11KqJdoObTFF4tQLEh0wMC9HH2YS26G\nIslokMcUit22xxEBNdtgQKQorJViokoxGeHxSbaqJQcpo0+B4jKlOqeexCbRLax8\nKEuVB2KYpLtm9v4ONQYwbr3JqDuL3ilXXnqpOAlY7HzGdm5Yt9JHG0ci4HZj03VL\nEnvubDUhAoGBAO41D2IDfeg/3s9QZ6iHmG/O9UOgBWqnNqx2Sh2D+37uR0FmDD41\nd05X4qw93wP3XoCe94slr/kHsOqaVCmyNyFCRF0U3z7QbUTJF0TsTHM4SLE9HIcH\nWEvL8YNCNKPQTlcRe7CmuJIrDfZNWB0F9Br1QUVoP49ykgnqBbzf0Mc5AoGBAMCw\nkktI4GooJSVaSLs/iUSuV2yLs+W7/k9jvUhXSMp5Q36gIpERB5rb4VwdzV9LbBKC\n1yobxDKch0gWflF1XRV6qvuR+Gzi0BElVIKeSj/gzZg+FSJZoe5jypN7Kxf7mX4J\nv8G4QTURMTdiPhSmc/fLqt8ceDzbGh+nReJ/4xCHAoGACtiPor7V9MUzt+zJS3sh\nDbY2pKWcmYaTjra0GTPxN45R4EBtPkfg7shBoeYPSXbx7plOXB+TK5uWCpiMTHm4\n2OLTiglxQMLstr0ROiooMPbXGHrX2a4T7x+SF4/kJbFOX9iD8T8mGEGtmRFcebXT\nr4aLOkXM3xMwYxMsv7TRJMECgYAkwgpGXlKhLaNYas6xGb+/4FpBFK1ux9wNnQNA\nx5XVOijMARRXBB6lRgjJn83LvgGRzm/pUn6tAPs1n0TdmTv2mv3/G6t+ag4zFyH2\nAOg9I09VGZLCiMLBTTwZwkdIPfDcAFQaSmH2E5+F5zHckpxQywN/qFivk0R6gVht\niuPwBQKBgQCIysi+2SfAYMAYd9V+aod6hZhtHjwkQAkAuOCeOo0iYkYeaVT3eRdK\nW24TCKG71rxdqh30OAxQrrsAUDqb/icN4d042EAnxt88lBl9IuuzgmLMZsa7ZJPQ\n98t5YPoC9gQh8dFGTMhbanfPTJPnh3AquEa76JfW2XEh87wUG57doQ==\n-----END RSA PRIVATE KEY-----"

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


parser = argparse.ArgumentParser(description='This script creates an SSL terminated LB')
parser.add_argument('fqdn', metavar='FQDN', type=valid_fqdn, nargs='+',
                   help='FQDN for the Load Balancer VIP')

args = parser.parse_args()
fqdn = args.fqdn[0]

path = os.path.expanduser("~/.rackspace_cloud_credentials")
try:
    pyrax.set_credential_file(path)
except pyrax.exceptions.AuthenticationFailed:
    print "Anthentication failed. Valid credentials needed in", path


# Creating isolated network
cnw = pyrax.cloud_networks

try:
    network = cnw.create("challenge11", cidr="192.168.0.0/24")
except pyrax.exceptions.NetworkCountExceeded as e:
    print "Error: %s" %e
    sys.exit(1)
print "Created New Cloud Network:", network

networks = network.get_server_networks()

# Building servers
cs = pyrax.cloudservers

image = [img for img in cs.images.list() if "CentOS" in img.name][0]
flavor = [flavor for flavor in cs.flavors.list() if flavor.ram == 512][0]

print "Creating %s Cloud servers..." %limit

servers = []
for i in range(limit):
    name = prefix + str(i)
    server = cs.servers.create(name, image.id, flavor.id, networks=networks)
    servers.append(server)

servers_copy = servers

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


# Adding SSL termination
lb.add_ssl_termination(
        securePort=443,
        enabled=True,
        secureTrafficOnly=False,
        certificate=cert,
        privatekey=key,
        )


# Attaching CBS volumes to servers
cbs = pyrax.cloud_blockstorage
mountpoint = "/dev/xvdb"
for server in servers_copy:
    vol = cbs.create(name=name, size=100, volume_type="SATA")
    vol.attach_to_instance(server, mountpoint=mountpoint)


