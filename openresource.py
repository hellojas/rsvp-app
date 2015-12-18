import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

import urlparse
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
    last_rsvp = ndb.StringProperty(indexed=True)

class Greeting(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    author = ndb.StructuredProperty(Author)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

def parseTimeToValue(Date, start, end):
        value =""
        dates = Date.split("/")
        value = str(dates[2]) + str(dates[0]) + str(dates[1])
        value += str("".join(start.split(":")))
        value += str("".join(end.split(":")))
        return value

class MainPage(webapp2.RequestHandler):

    def get(self):
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        greetings_query = Greeting.query(
            ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
        greetings = greetings_query.fetch(10)

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
        else:
            resources_user = []


        template_values = {
            'user': user,
            'greetings': greetings,
            'guestbook_name': urllib.quote_plus(guestbook_name),
            'url': url,
            'url_linktext': url_linktext,
            'resources_all':resources_all,
            'resources_user':resources_user,
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

        resource.last_rsvp = parseTimeToValue(
            res_date, res_start, res_end)

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

        template_values = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'resource': resource,
        }

        template = JINJA_ENVIRONMENT.get_template('view.html')
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

        # if users.get_current_user():
        #     resource.creator = Author(
        #         identity = user.user_id(),
        #         email=user.email())

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



        # template = JINJA_ENVIRONMENT.get_template('index.html')
        # self.response.write(template.render(template_values))
        self.redirect('/')

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
            # def post(self):
    #     user = users.get_current_user()

    #     if user:
    #         url = users.create_logout_url(self.request.uri)
    #         url_linktext = 'Logout'
    #     else:
    #         url = users.create_login_url(self.request.uri)
    #         url_linktext = 'Login'


    #     key = ndb.Key(urlsafe=self.request.get('tkey'))
    #     tag = key.get()

    #     resource_query_tag = Resource.query()(Resource.tag.label = tag.label)
    #     resources_tag  = resource_query_tag.fetch()

    #     template_values = {
    #         'user': user,
    #         'url': url,
    #         'url_linktext': url_linktext,
    #         'resources_tag':resources_user,
    #     }

    #     self.redirect('/')

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/add', AddResourcePage),
    ('/submit', Guestbook),
    ('/view', ViewResourcePage),
    ('/edit', EditResourcePage),
    ('/tags',TagsQueryPage)

], debug=True)