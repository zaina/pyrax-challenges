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

""" This script screates a Cloud Database instance, a database and a user
	who can connect to it """

import pyrax
import os
import time
import sys
import argparse
import random, string

def valid (flavor):
	flavors = ['512MB', '1G', '2G', '4G']
	if flavor not in flavors :
		raise argparse.ArgumentTypeError("%s is not a valid flavor, available are 512MB, 1G, 2G, 4G." % flavor)
	return flavor

parser = argparse.ArgumentParser(description='This script creates a Cloud Database instance,\
			a database and a user who can connect to it')
parser.add_argument('instance', metavar='InstanceName', type=str, nargs='+', help='Instance name')
parser.add_argument('flavor', metavar='InstanceFlavor', type=valid, nargs='+', 
				help='Instance Flavor: 512MB, 1G, 2G, 4G')
parser.add_argument('volume', metavar='InstanceVolume', type=int, nargs='+', choices=xrange(1, 150),
				 help='Instance volume: range 1-150 G')
parser.add_argument('db', metavar='DBName', type=str, nargs='+', help='MySQL DB name')
parser.add_argument('user', metavar='Username', type=str, nargs='+', help='Username')
args = parser.parse_args()

instance = args.instance[0]
flavor = args.flavor[0]
volume = args.volume[0]
db = args.db[0]
user = args.user[0]

credentials_file = os.path.expanduser("~/.rackspace_cloud_credentials")
try:
	pyrax.set_credential_file(credentials_file)
except pyrax.exceptions.AuthenticationFailed:
	print "Anthentication failed. Valid credentials needed in ~/.rackspace_cloud_credentials"

cdb = pyrax.cloud_databases

flavors = cdb.list_flavors()

for flv in flavors:
	if flavor in flv.name:
		flavor = flv
		break
if not flavor :
	print "No valid flavor selected"
	sys.exit(1)

print "Creating instance %s with size %s and flavor %s..." %(instance, volume, flavor.name)
inst = cdb.create(instance, flavor=flavor, volume=volume)

while "ACTIVE" not in inst.status:
	inst.get()
	time.sleep(1)
print "Instance Name:", inst.name
print "Instance Status:", inst.status
print "Instance Hostname:", inst.hostname

database = inst.create_database(db)
print "DataBase Name:", database.name

# Generate Random password
myrg = random.SystemRandom()
length = 10
alphabet = string.letters[0:52] + string.digits
password = str().join(myrg.choice(alphabet) for _ in range(length))

dbuser = inst.create_user(user, password, database_names=[database])
print "Username:", dbuser.name
print "Password:", password
