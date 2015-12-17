import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

import cgi

# from app import Author
# from app import Reservation
# from app import Resource
# from app import Time

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

DEFAULT_GUESTBOOK_NAME = 'default_guestbook'


# We set a parent key on the 'Greetings' to ensure that they are all
# in the same entity group. Queries across the single entity group
# will be consistent. However, the write rate should be limited to
# ~1/second.

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity.

    We use guestbook_name as the key.
    """
    return ndb.Key('Guestbook', guestbook_name)

# class Time():
#     def __init__(self, Date, start, end):
#         self.Date = None
#         self.start = None
#         self.end = None

#     def __repr__(self):
#         return "[Availability] %s from %s until %s" %(self.Date, self.start, self.end)

class Time(ndb.Model):
    Date = ndb.StringProperty(indexed=False)
    start = ndb.StringProperty(indexed=False)
    end = ndb.StringProperty(indexed=False)
    # def __repr__(self):
        # return "[Availability] %s from %s until %s" %(self.Date.toString(), self.start, self.end)
    def getValue():
        value = ""
        dates = self.Date.split("/")
        value = str(dates[2]) + str(dates[p]) + str(dates[1])

class Tag(ndb.Model):
    name = ndb.StringProperty()

class Author(ndb.Model):
    """Sub model for representing an author."""
    identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)

class Reservation(ndb.Model):
    user_name = ndb.StructuredProperty(Author)
    resource = ndb.StringProperty(indexed=False)
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

class Resource(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    creator = ndb.StructuredProperty(Author)
    name = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
    tags = ndb.StructuredProperty(Tag, repeated=True)
    availability = ndb.StructuredProperty(Time)
    last_rsvp = ndb.StringProperty(indexed=True))


class Greeting(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    author = ndb.StructuredProperty(Author)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)


class MainPage(webapp2.RequestHandler):

    def get(self):
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        greetings_query = Greeting.query(
            ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
        greetings = greetings_query.fetch(10)


        resource_query = Resource.query()
        resources = resource_query.fetch(10).order(-Resource.last_rsvp)

        print "resources?"

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'user': user,
            'greetings': greetings,
            'guestbook_name': urllib.quote_plus(guestbook_name),
            'url': url,
            'url_linktext': url_linktext,
            'resources':resources,
            'resources_size':len(resources),
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
                identity = users.get_current_user().user_id(),
                email=users.get_current_user().email())

        resource.name = cgi.escape(self.request.get('resourceName'))

        resource.availability = Time(
            Date = cgi.escape(self.request.get('date')),
            start = cgi.escape(self.request.get('timeStart')),
            end = cgi.escape(self.request.get('timeEnd')))

        resource.put()


        # greeting.content = self.request.get('content')
        # greeting.put()

        class test():
            inside = "blah"

        a = test()

        template_values = {
            'resource_object': resource,
            'test': a,
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
        }



        # template = JINJA_ENVIRONMENT.get_template('index.html')
        # self.response.write(template.render(template_values))
        self.redirect('/')

class Guestbook(webapp2.RequestHandler):

    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each
        # Greeting is in the same entity group. Queries across the
        # single entity group will be consistent. However, the write
        # rate to a single entity group should be limited to
        # ~1/second.
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        greeting = Greeting(parent=guestbook_key(guestbook_name))

        if users.get_current_user():
            greeting.author = Author(
                    identity=users.get_current_user().user_id(),
                    email=users.get_current_user().email())

        greeting.content = self.request.get('content')
        greeting.put()

        query_params = {'guestbook_name': guestbook_name}
        self.redirect('/?' + urllib.urlencode(query_params))


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/add', AddResourcePage),
    ('/submit', Guestbook)
], debug=True)