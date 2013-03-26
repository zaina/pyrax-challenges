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

""" This script uploads the contents of a directory to a Cloud Files 
	Container """

import pyrax
import os
import time
import sys
import argparse

def valid (directory):
	#print "Checking " + directory
	if not os.path.exists(directory):
		raise argparse.ArgumentTypeError("%s is not a valid directory" % directory)
	return directory

parser = argparse.ArgumentParser(description='This script uploads \
			the contents of a directory to a Cloud Files Container')
parser.add_argument('directory', metavar='DirectoryPath', type=valid, nargs='+',
                   help='Full path to the directory to upload')
parser.add_argument('container', metavar='ContainerName', type=str, nargs='+',
                   help='Name of the Cloud Files container, if it \
					doesn\'t exist it will be created.')
args = parser.parse_args()
#print(args.accumulate(args.integers))
container_name = args.container[0]
directory_path = args.directory[0]

credentials_file = os.path.expanduser("~/.rackspace_cloud_credentials")
try:
	pyrax.set_credential_file(credentials_file)
except pyrax.exceptions.AuthenticationFailed:
	print "Anthentication failed. Valid credentials needed in ~/.rackspace_cloud_credentials"

cf = pyrax.cloudfiles

files_list = os.listdir(directory_path)
print "Uploading files list: %s " %files_list

upload_key, total_bytes = cf.upload_folder(directory_path, container_name)
print "Total bytes to upload:", total_bytes
uploaded = 0
while uploaded < total_bytes:
	uploaded = cf.get_uploaded(upload_key)
	print "Progress: %4.2f%%" % ((uploaded * 100.0) / total_bytes)
	time.sleep(1)

