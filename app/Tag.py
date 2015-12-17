from google.appengine.ext import ndb

class Tag(ndb.Model):
	name = ndb.StringProperty()