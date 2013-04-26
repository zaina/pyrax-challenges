#!/usr/bin/env python

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
#

""" This script creates a new A record when passed a FQDN and IP address """

import pyrax
import os
import time
import sys
import argparse
import re

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

parser = argparse.ArgumentParser(description='This script creates a new A record \
    		when passed a FQDN and IP address')
parser.add_argument('fqdn', metavar='FQDN', type=valid_fqdn, nargs='+', help='FQDN for the A record')
parser.add_argument('ip', metavar='IPAddress', type=str, nargs='+', help='IP Address')
args = parser.parse_args()

fqdn = args.fqdn[0]
ip = args.ip[0]

path = os.path.expanduser("~/.rackspace_cloud_credentials")
try:
    pyrax.set_credential_file(path)
except pyrax.exceptions.AuthenticationFailed:
    print "Anthentication failed. Valid credentials needed in", path 

dns = pyrax.cloud_dns
domain, ext = fqdn.split('.')[-2:]
zone = '.'.join(fqdn.split('.')[-2:])

try:
    domain = dns.find(name=zone)
except pyrax.exceptions.NotFound:
    print "Domain name '%s' not found" %zone
    sys.exit(1)

a_record = {"type": "A",
        "name": fqdn,
        "data": ip,
        "ttl": 300}

try:
    result = domain.add_records(a_record)
except pyrax.exceptions.BadRequest as e:
    print "A record creation failed: Bad Request %s" %e
    sys.exit(1)
except pyrax.exceptions.DomainRecordAdditionFailed as e:
    print "A record creation failed: %s" %e
    sys.exit(1)
print "A record added successfully"
