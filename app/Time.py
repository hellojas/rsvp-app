from datetime import datetime, date, time

class Time():
	def __init__(self, Date, start, end):
		self.Date = None
		self.start = None
		self.end = None
		if not self.validate_all(Date, start, end):
			print "invalid date time!"

	def validate_all(self, Date, start, end):
		valid_date = self.validate_date(Date)
		valid_start = self.validate_time(start)
		valid_end = self.validate_time(end)

		# ERROR not valid date or start/end time
		if not valid_date and not valid_start and not valid_end:
			return False

		# ERROR end time before start time
		if valid_start > valid_end:
			return False

		# ERROR date selected before today
		if datetime.combine(valid_date,valid_start) < datetime.now():
			return False

		self.Date = valid_date
		self.start = valid_start
		self.end = valid_end

		return True

	def in_timespan(self, new_time):
		return self.Date == new_time.Date and self.start < new_time.start < new_time.end < self.end



	'''
	assume yyyy/mm/dd
	'''
	def validate_date(self, Date):
		date_arr = [int(d) for d in Date.split("/")]
		try:
			return date(date_arr[0], date_arr[1], date_arr[2])
		except:
			return None

	'''
	assume HH:MM
	'''
	def validate_time(self, mytime):
		time_arr = [int(t) for t in mytime.split(":")]
		try:
			return (time(time_arr[0], time_arr[1]))
		except:
			return None

	def __str__(self):
		return self.Date.strftime("%A, %d. %B %Y") + " from " + self.start.strftime("%I:%M%p") + " to " + self.end.strftime("%I:%M%p")

def test():
	# err before today
	print "test1"
	mytime = Time("2014/06/02", "1:30","13:40")
	
	# err wrong date
	print "test2"
	mytime = Time("201/5/2", "1:30","13:30")

	# valid
	print "test3"
	mytime = Time("2018/5/2", "1:0","13:30")
	print mytime

	# valid
	print "test4"
	mytime = Time("2018/5/2", "2:00","13:30")
	print mytime
	print "should be true: " + str(mytime.in_timespan(Time("2018/5/2", "3:00","4:00")))
 	print "should be false: " + str(mytime.in_timespan(Time("2018/5/3", "3:00","4:00")))
 	print "should be false: " + str(mytime.in_timespan(Time("2018/5/2", "1:59","4:00")))

if __name__ == "__main__":
	test()
