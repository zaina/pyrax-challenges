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

""" Write an application that will create a route in mailgun so that 
    when an email is sent to <username>@apichallenges.mailgun.org 
    it calls your Challenge 1 script that builds 3 servers. 
"""	
import os
import requests
from werkzeug.datastructures import MultiDict

path = os.path.expanduser("~/.mailgunapi")
auth = open(path, 'r')
print auth.read()

def create_route():
    return requests.post(
        "https://api.mailgun.net/v2/routes",
        auth=("api", auth.read()),
        data=MultiDict([("priority", 1),
                        ("description", "Challenge1 route"),
                        ("expression", "match_recipient('.*@apichallenges.mailgun.org')"),
                        ("action", "forward('http://cldsrvr.com/challenge1')"),
                        ("action", "stop()")]))

print create_route()
