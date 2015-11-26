from base import BaseHandler
from models import User
from google.appengine.ext import ndb
from webapp2_extras.appengine.auth.models import Unique
import logging

class AlreadyHandler(BaseHandler):
	def post(self, *args, **kwargs):
		check_type = kwargs['type']
		

		if check_type == 'u':
			username = self.request.body
			logging.info(username)
			key = ndb.Key(Unique, "User.auth_id:"+username)
			logging.info(key)
			exists = key.get()
			logging.info(exists)
			if exists:
				self.response.out.write("true")
			else:
				self.response.out.write("false")

		if check_type == 'e':
			email = self.request.body
			logging.info(email)
			key = ndb.Key(Unique, "User.email:"+email)
			logging.info(key)
			exists = key.get()
			logging.info(exists)
			if exists:
				self.response.out.write("true")
			else:
				self.response.out.write("false")