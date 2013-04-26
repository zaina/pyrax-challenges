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

""" Write an application that nukes everything in your Cloud Account.
It should:
Delete all Cloud Servers
Delete all Custom Images
Delete all Cloud Files Containers and Objects
Delete all Databases
Delete all Networks
Delete all CBS Volumes 
"""	

import pyrax
import os
import time

credentials_file = os.path.expanduser("~/.rackspace_cloud_credentials")
try:
    pyrax.set_credential_file(credentials_file)
except pyrax.exceptions.AuthenticationFailed:
    print "Anthentication failed. Valid credentials needed in ~/.rackspace_cloud_credentials"

# Cloud Servers
for region in ['ORD', 'DFW']: 
    cs = pyrax.connect_to_cloudservers(region=region)
    for server in cs.servers.list():
        print "Removing Cloud Server:", server.name
        server.delete()

# Custom Images
for region in ['ORD', 'DFW']: 
    cs = pyrax.connect_to_cloudservers(region=region)
    for snap in cs.list_snapshots():
        print "Removing Snapshot:", snap.name
        snap.delete()

# Cloud Files
cf = pyrax.cloudfiles
containers = cf.get_all_containers()
for container in containers:
    print container.name
    objs = container.get_objects()
    if not objs:
        print "Container empty, removing", container.name
        container.delete()
    else:
        for obj in objs:
            print "Removing Object:", obj.name
            obj.delete()
        container.delete()


# Databases
for region in ['ORD', 'DFW']:
    cdb = pyrax.connect_to_cloud_databases(region=region)
    for instance in cdb.list():
        print "Removing instance", instance.name
        instance.delete()

# CBS Volumes
for region in ['ORD', 'DFW']:
    cds = pyrax.connect_to_cloud_blockstorage(region=region)
    for volume in cds.list():
        print "Removing volume", volume.name
        volume.delete()


# Networks
cnw = pyrax.cloud_networks
for network in cnw.list():
    if network.id == "11111111-1111-1111-1111-111111111111" or network.id == "00000000-0000-0000-0000-000000000000":
        print "Can't remove default network", network.id
    else:
        print "Removing network", network.name
        network.delete()


