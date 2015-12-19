import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

import urlparse
import cgi

import datetime

from pytz.gae import pytz

from lxml import etree

# from app import Author
# from app import Reservation
# from app import Resource
# from app import Time

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class Time(ndb.Model):
    Date = ndb.StringProperty(indexed=False)
    start = ndb.StringProperty(indexed=False)
    end = ndb.StringProperty(indexed=False)

class Tag(ndb.Model):
    label = ndb.StringProperty(indexed=True)

    def __repr__(self):
        return self.label

class Author(ndb.Model):
    """Sub model for representing an author."""
    identity = ndb.StringProperty(indexed=True)
    email = ndb.StringProperty(indexed=True)

class Resource(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    creator = ndb.StructuredProperty(Author)
    name = ndb.StringProperty(indexed=False)
    tags = ndb.StructuredProperty(Tag, repeated=True)
    availability = ndb.StructuredProperty(Time)
    last_rsvp = ndb.DateTimeProperty(auto_now_add=True)

class Reservation(ndb.Model):
    user = ndb.StructuredProperty(Author)
    created = ndb.DateTimeProperty(auto_now_add=True)
    time = ndb.StructuredProperty(Time)
    duration = ndb.StringProperty(indexed=False)
    sort_value = ndb.StringProperty()
    resource_key = ndb.StringProperty(indexed=True)
    resource_name = ndb.StringProperty(indexed=False)

def parseTimeToValue(Date, start, end):
        value = ""
        dates = Date.split("/")
        value = str(dates[2]) + str(dates[0]) + str(dates[1])
        value += str("".join(start.split(":")))
        value += str("".join(end.split(":")))
        return value

def parseHourMinToValue(hr_min):
    return ((int(hr_min[0:2]) * 60) + int(hr_min[3:5]))

def parseTimeToDuration(start, end):
        duration_str= ""
        duration_value = (int(end[0:2]) * 60 + int(end[3:5])) - (int(start[0:2]) * 60 + int(start[3:5]))
        if duration_value >= 60:
            hours = duration_value/60

            if duration_value % 60 == 0:
                hours = duration_value/60
                duration_str = "%dH" %(hours)
            else:
                minutes = duration_value - (hours*60)
                duration_str = "%dH%dM" %(hours,minutes)
        else:
            duration_str = "%dM" %duration_value 
        return duration_str

def cleanReservations():
    rsvp_all_query = Reservation.query()
    rsvps_all = rsvp_all_query.fetch()
    tz = pytz.timezone('US/Eastern')

    datetime_obj = tz.localize(datetime.datetime.now())
    year = datetime_obj.timetuple()[0]
    month = datetime_obj.timetuple()[1]
    day = datetime_obj.timetuple()[2]
    hour = datetime_obj.timetuple()[3]
    minutes = datetime_obj.timetuple()[4]

    for rsvp in rsvps_all:
        dates = rsvp.time.Date.split("/")
        rsvp_mon = int(dates[0])
        rsvp_day = int(dates[1])
        rsvp_year = int(dates[2])
        rsvp_hour = int(rsvp.time.end[0:2])
        rsvp_min = int(rsvp.time.end[3:5])

        delete_rsvp = False

        if rsvp_year == year:
            if rsvp_mon < month:
                delete_rsvp = True
            else:
                if rsvp_day > day:
                    delete_rsvp = True
                else:
                    if rsvp_hour < hour:
                        delete_rsvp = True
                    else:
                        if rsvp_min < minutes:
                            delete_rsvp = True

        if delete_rsvp:
            key = rsvp.key
            key.delete()

def validReservation(res_start_val, res_end_val, rsvps_all):
    for existing_rsvp in rsvps_all:
        blocked_start = parseHourMinToValue(existing_rsvp.time.start)
        blocked_end = parseHourMinToValue(existing_rsvp.time.end)

        # equal
        if res_start_val == blocked_start or res_end_val == blocked_end:
            return False

        # within blocked time
        if (res_start_val > blocked_start) and (res_end_val < blocked_end):
            return False

        # starts before block but ends after block
        if (res_start_val < blocked_start) and (res_end_val > blocked_start):
            return False

        # ends before block but starts within block
        if  (res_start_val < blocked_end) and (res_end_val > blocked_end):
            return False

    return True

def dumpToRss(rsvps_user):
    root = etree.Element('root')
    # root.append(etree.Element('child'))
    # another child with text
    for rsvp in rsvps_user:
        child = etree.Element('child')
        child.text = rsvp.resource_name
        root.append(child)
    s = etree.tostring(root, pretty_print=True)

    return s

class MainPage(webapp2.RequestHandler):

    def get(self):

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        cleanReservations()

        resource_query_all = Resource.query().order(-Resource.last_rsvp)
        resources_all = resource_query_all.fetch()

        if user:

            resource_query_user = Resource.query(
                Resource.creator == Author(
                    identity = user.user_id(),
                    email=user.email())).order(Resource.last_rsvp)
                
            resources_user = resource_query_user.fetch()

            rsvp_user_query = Reservation.query(
                Reservation.user == Author(
                        identity = user.user_id(),
                        email=user.email())).order(Reservation.sort_value)
            rsvps_user = rsvp_user_query.fetch()
        else:
            resources_user = []
            rsvps_user = []


        datetime_obj = datetime.datetime.now()
        year = datetime_obj.timetuple()[0]
        month = datetime_obj.timetuple()[1]
        day = datetime_obj.timetuple()[2]
        hour = datetime_obj.timetuple()[3]
        minutes = datetime_obj.timetuple()[4]


        template_values = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'resources_all':resources_all,
            'resources_user':resources_user,
            'rsvps_user': rsvps_user,
            'now':datetime.datetime.now()
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

class AddResourcePage(webapp2.RequestHandler):

    def get(self):

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template('add.html')
        self.response.write(template.render(template_values))

    def post(self):
        user = users.get_current_user()

        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        create_resource_values = {"resourceName":cgi.escape(self.request.get('resourceName')), 
            "date":cgi.escape(self.request.get('date')),
            "timeStart":cgi.escape(self.request.get('timeStart')),
            "timeEnd":cgi.escape(self.request.get('timeEnd')),
            }

        ## create new resource object

        resource = Resource()

        if users.get_current_user():
            resource.creator = Author(
                identity = user.user_id(),
                email=user.email())

        resource.name = cgi.escape(self.request.get('resourceName'))

        res_date = cgi.escape(self.request.get('date'))
        res_start = cgi.escape(self.request.get('timeStart'))
        res_end = cgi.escape(self.request.get('timeEnd'))

        resource.availability = Time(
            Date = res_date,
            start = res_start,
            end = res_end)

        # resource.last_rsvp = parseTimeToValue(
        #     res_date, res_start, res_end)

        res_tags = cgi.escape(self.request.get('tags')).split(",")

        for tag_str in res_tags:
            tag = Tag(label = tag_str)
            tag.put()
            resource.tags.append(tag)

        resource.put()


        resource_query_all = Resource.query().order(-Resource.last_rsvp)
        resources_all = resource_query_all.fetch()

        resource_query_user = Resource.query(
            Resource.creator == Author(
                identity = user.user_id(),
                email=user.email()))
            
        resources_user = resource_query_user.fetch()


        template_values = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'resources_all':resources_all,
            'resources_user':resources_user,
        }

        self.redirect('/')

class ReserveResourcePage(webapp2.RequestHandler):

    def get(self):

        key = ndb.Key(urlsafe=self.request.get('rkey'))
        resource = key.get()

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'


        rsvp_all_query = Reservation.query(
            Reservation.resource_key == key.urlsafe()).order(Reservation.sort_value)
        rsvps_all = rsvp_all_query.fetch()


        template_values = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'resource': resource,
            'rsvps_all':rsvps_all
        }

        template = JINJA_ENVIRONMENT.get_template('reserve.html')
        self.response.write(template.render(template_values))

    def post(self):
        user = users.get_current_user()

        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'


        key = ndb.Key(urlsafe=self.request.get('rkey'))
        resource = key.get()

        rsvp_success = "False"


        rsvp_all_query = Reservation.query(
            Reservation.resource_key == key.urlsafe()).order(Reservation.sort_value)
        rsvps_all = rsvp_all_query.fetch()

        res_date = resource.availability.Date
        res_start = cgi.escape(self.request.get('timeStart'))
        res_end = cgi.escape(self.request.get('timeEnd'))

        res_start_val = parseHourMinToValue(res_start)
        res_end_val = parseHourMinToValue(res_end)
        res_start_avail_val = parseHourMinToValue(resource.availability.start)
        res_end_avail_val = parseHourMinToValue(resource.availability.end)

        if validReservation(res_start_val, res_end_val, rsvps_all):
        ## create new reservation object

            resource.last_rsvp =  datetime.datetime.now() 

            reservation = Reservation()

            if users.get_current_user():
                reservation.user = Author(
                    identity = user.user_id(),
                    email=user.email())

            reservation.resource_key = key.urlsafe()
            reservation.resource_name = resource.name

            reservation.time = Time(
                Date = res_date,
                start = res_start,
                end = res_end)

            reservation.duration = parseTimeToDuration(res_start,res_end)
            reservation.sort_value = parseTimeToValue(res_date, res_start, res_end)

            reservation.put()
            resource.put()
            rsvp_success = "True"


        ## get page sections

        resource_query_all = Resource.query().order(-Resource.last_rsvp)
        resources_all = resource_query_all.fetch()

        resource_query_user = Resource.query(
            Resource.creator == Author(
                identity = user.user_id(),
                email=user.email()))
            
        resources_user = resource_query_user.fetch()


        rsvp_user_query = Reservation.query(
            Reservation.user == Author(
                    identity = user.user_id(),
                    email=user.email())).order(Reservation.sort_value)
        rsvps_user = rsvp_user_query.fetch()

        template_values = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'resources_all':resources_all,
            'resources_user':resources_user,
            'rsvps_user': rsvps_user,
            'rsvp_success':rsvp_success,
        }


        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

class ViewResourcePage(webapp2.RequestHandler):

    def get(self):

        key = ndb.Key(urlsafe=self.request.get('rkey'))
        resource = key.get()

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        rsvp_all_query = Reservation.query(
            Reservation.resource_key == key.urlsafe()).order(Reservation.sort_value)
        rsvps_all = rsvp_all_query.fetch()

        template_values = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'resource': resource,
            'rsvps_all':rsvps_all
        }

        template = JINJA_ENVIRONMENT.get_template('view.html')
        self.response.write(template.render(template_values))

class ResourceRssPage(webapp2.RequestHandler):

    def get(self):

        key = self.request.get('ukey')
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        resource_query_user = Resource.query(
            Resource.creator == Author(identity = key)).order(-Resource.last_rsvp)
        resources_user = resource_query_user.fetch()


        rsvp_user_query = Reservation.query(
            Reservation.user == Author(
                    identity = key)).order(Reservation.sort_value)
        rsvps_user = rsvp_user_query.fetch()

        template_values = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'resources_user':resources_user,
            'rsvps_user': rsvps_user,
            'username': key
        }

        template = JINJA_ENVIRONMENT.get_template('user.html')
        self.response.write(template.render(template_values))


class ViewUserPage(webapp2.RequestHandler):

    def get(self):

        key = self.request.get('ukey')
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        resource_query_user = Resource.query(
            Resource.creator == Author(identity = key)).order(-Resource.last_rsvp)
        resources_user = resource_query_user.fetch()


        rsvp_user_query = Reservation.query(
            Reservation.user == Author(
                    identity = key)).order(Reservation.sort_value)
        rsvps_user = rsvp_user_query.fetch()

        template_values = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'resources_user':resources_user,
            'rsvps_user_rss': rsvps_user_rss,
            'username': key
        }

        template = JINJA_ENVIRONMENT.get_template('user.html')
        self.response.write(template.render(template_values))

class EditResourcePage(webapp2.RequestHandler):

    def get(self):

        key = ndb.Key(urlsafe=self.request.get('rkey'))
        resource = key.get()

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'resource': resource,
        }

        template = JINJA_ENVIRONMENT.get_template('edit.html')
        self.response.write(template.render(template_values))


    def post(self):
        user = users.get_current_user()

        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        key = ndb.Key(urlsafe=self.request.get('rkey'))
        resource = key.get()

        resource.name = cgi.escape(self.request.get('resourceName'))

        res_date = cgi.escape(self.request.get('date'))
        res_start = cgi.escape(self.request.get('timeStart'))
        res_end = cgi.escape(self.request.get('timeEnd'))

        resource.availability = Time(
            Date = res_date,
            start = res_start,
            end = res_end)

        resource.last_rsvp = parseTimeToValue(
            res_date, res_start, res_end)

        res_tags = cgi.escape(self.request.get('tags')).split(",")
        resource.tags[:] = []

        for tag_str in res_tags:
            tag = Tag(label = tag_str)
            resource.tags.append(tag)

        resource.put()


        resource_query_all = Resource.query().order(-Resource.last_rsvp)
        resources_all = resource_query_all.fetch()

        resource_query_user = Resource.query(
            Resource.creator == Author(
                identity = user.user_id(),
                email=user.email()))
            
        resources_user = resource_query_user.fetch()


        template_values = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'resources_all':resources_all,
            'resources_user':resources_user,
        }


        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

class TagsQueryPage(webapp2.RequestHandler):

    def get(self):

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        if self.request.get('label'):
            label = cgi.escape(self.request.get('label'))
            resource_query_tag = Resource.query(
                Resource.tags == Tag(label=label))
            resources_tag  = resource_query_tag.fetch()

            template_values = {
                'user': user,
                'url': url,
                'url_linktext': url_linktext,
                'resources_tag':resources_tag,
                'tag':label
            }

            template = JINJA_ENVIRONMENT.get_template('tags.html')
            self.response.write(template.render(template_values))
        else: 
            template_values = {
                'user': user,
                'url': url,
                'url_linktext': url_linktext,
                'resources_tag':None,
            }
            template = JINJA_ENVIRONMENT.get_template('tags.html')
            self.response.write(template.render(template_values))    


class DeleteReservation(webapp2.RequestHandler):

    def get(self):
        delete_success = "False"

        try:
            key = ndb.Key(urlsafe=self.request.get('rsvpkey'))
            key.delete()
            delete_success = "True"
        except:
            delete_success = "False"


        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'


        resource_query_all = Resource.query().order(Resource.last_rsvp)
        resources_all = resource_query_all.fetch()

        if user:

            resource_query_user = Resource.query(
                Resource.creator == Author(
                    identity = user.user_id(),
                    email=user.email())).order(Resource.last_rsvp)
                
            resources_user = resource_query_user.fetch()

            rsvp_user_query = Reservation.query(
                Reservation.user == Author(
                        identity = user.user_id(),
                        email=user.email())).order(Reservation.sort_value)
            rsvps_user = rsvp_user_query.fetch()
        else:
            resources_user = []
            rsvps_user = []


        template_values = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'resources_all':resources_all,
            'resources_user':resources_user,
            'rsvps_user': rsvps_user,
            'delete_success':delete_success
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/add', AddResourcePage),
    ('/view', ViewResourcePage),
    ('/edit', EditResourcePage),
    ('/tags',TagsQueryPage),
    ('/reserve', ReserveResourcePage),
    ('/user', ViewUserPage),
    ('/delete', DeleteReservation),
    ('/rss', ResourceRssPage)

], debug=True)