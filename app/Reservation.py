from app import Time

class Reservation(ndb.Model):
	# def __init__(self, user_name, resource, rsvp_time):
	# 	self.user_name = user_name
	# 	self.resource = resource
	# 	self.rsvp_time = rsvp_time
	user_name = ndb.StructuredProperty(User)
    resource = ndb.StringProperty(indexed=False)
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)
    rsvp = ndb.StructuredProperty(Time)

