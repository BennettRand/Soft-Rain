#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#	 http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import os.path
import json
import urllib2
import pywapi
import cgi

from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.api import taskqueue

class Device(ndb.Model):
	name = ndb.StringProperty(indexed=True,required=True,default="")
	uuid = ndb.StringProperty(indexed=True,required=True)
	type = ndb.StringProperty(indexed=True,required=True,default="")
	updated = ndb.BooleanProperty(required=True,default=False)
	settings = ndb.JsonProperty(required=True,default={})
	upload = ndb.JsonProperty(repeated=True,compressed=True)
	loc = ndb.GeoPtProperty()
	date = ndb.DateTimeProperty(auto_now_add=True)
	
	@classmethod
	def query_book(cls, ancestor_key):
		return cls.query(ancestor=ancestor_key).order(-cls.date)

def _temp_triple_k(k):
	c = k-273.15
	f = 9/(5*c)+32
	return (k,c,f)

def _get_weather_for(ip):
	loc = json.loads(urllib2.urlopen("http://freegeoip.net/json/"+ip).read())
	w = urllib2.urlopen("http://api.openweathermap.org/data/2.5/weather?lat={}&lon={}".format(loc['latitude'], loc['longitude'])).read()	#pywapi.get_weather_from_weather_com(loc['zipcode'])
	return json.loads(w)

def _check_complete(d):
	if d.name == "":
		return False
	if d.type == "":
		return False
	if d.loc == None:
		return False
	return True

class HeartbeatHandler(webapp2.RequestHandler):
	def get(self):
		error = [False, []]
		q = cgi.parse_qs(self.request.environ['QUERY_STRING'])
		devices = []
		
		if 'uuid' in q:
			device = Device.query(Device.uuid == q['uuid'][0])
			
			devices = [d for d in device]
		
		if len(devices) > 0:
			d = devices[0]
			change = False
			
			if _check_complete(d) and 'name' not in q and 'type' not in q:
				self.response.set_status(304)
				return
			
			if d.loc == None:
				ip = self.request.environ['REMOTE_ADDR']
				loc = json.loads(urllib2.urlopen("http://freegeoip.net/json/"+ip).read())
				
				d.loc = ndb.GeoPt(loc['latitude'], loc['longitude'])
				change = True
			
			if 'name' in q:
				d.name = q['name'][0]
				change = True
				
			if 'type' in q:
				d.type = q['type'][0]
				change = True
				
			if change:
				d.put()
				
				if _check_complete(d):
					self.response.set_status(201)
				else:
					self.response.set_status(202)
			else:
				if _check_complete(d):
					self.response.set_status(304)
				else:
					self.response.set_status(202)
				
		elif len(devices) == 0:
			d = Device(uuid = q['uuid'][0])
			d.put()
			self.response.set_status(202)
			
		else:
			self.response.write(q)
			self.response.set_status(400)
		return

class MainHandler(webapp2.RequestHandler):
	def get(self):
		dir = "./templates/"
		
		onlyfiles = [ f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir,f)) ]
		templates = {f.rstrip(".html"): open(dir+f).read() for f in onlyfiles}
		
		# self.response.headers['Content-Type'] = 'application/json'
		self.response.write(templates['main'])
		self.response.write(_get_weather_for(self.request.environ['REMOTE_ADDR']))
		return

app = webapp2.WSGIApplication([
	('/', MainHandler),
	('/poll', HeartbeatHandler)
], debug=True)
