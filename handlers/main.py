from base import BaseHandler
import os
from google.appengine.ext.webapp import template
import logging

class MainHandler(BaseHandler):
	def get(self):
		self.render_template('index.html')
