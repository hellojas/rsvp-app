import Time
from google.appengine.ext import ndb

class Tag(ndb.Model):
	name = ndb.StringProperty()

class Resource(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    author = ndb.StructuredProperty(Author)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
    tags = ndb.StructuredProperty(Tag, repeated=True)

# class Resource(ndb.Model):
# 	name = ndb.StringProperty()
# 	availability = StructuredProperty(Time)
#     tags = ndb.StructuredProperty(Tag, repeated=True)
#     rsvps = ndb.StructuredProperty(Reservation, repeated=True)


# 	def __init__(self, name, avail, tags):
# 		self.name = name
# 		self.availability = availability
# 		self.tags = tags
# 		self.rsvps = [] 
# 		self.owner = None

	# def set_owner(self, owner):
	# 	self.owner = owner

	# def add_reservation(self, new_time):
	# 	if self.availability.in_timespan(new_time):
	# 		self.rsvp.append(new_time)

	# def get_desc_times(self):
	# 	return sorted(self.rsvps)
