import Time

class Resource():
	def __init__(self, name, avail, tags):
		self.name = name
		self.availability = availability
		self.tags = tags
		self.rsvps = [] 
		self.owner = None

	def set_owner(self, owner):
		self.owner = owner

	def add_reservation(self, new_time):
		if self.availability.in_timespan(new_time):
			self.rsvp.append(new_time)

	def get_desc_times(self):
		return sorted(self.rsvps)
