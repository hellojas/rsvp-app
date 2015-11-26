import webapp2

class HelloWebapp2(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello, webapp2!')

app = webapp2.WSGIApplication([
    ('/', HelloWebapp2),
], debug=True)

#!/usr/bin/env python
import webapp2
import logging
from webapp2_extras import auth
from webapp2_extras import sessions
from handlers import *


config = {
  'webapp2_extras.auth': {
    'user_model': 'models.User',
    'user_attributes': ['name']
  },
  'webapp2_extras.sessions': {
    'secret_key': 'secret_key'
  }
}

app = webapp2.WSGIApplication([
    webapp2.Route('/', main.MainHandler, name='home'),
    webapp2.Route('/signup', signup.SignupHandler),
    webapp2.Route('/already/<type:e|u>',already.AlreadyHandler),
    webapp2.Route('/<type:v|p>/<user_id:\d+>-<signup_token:.+>', handler=verification.VerificationHandler, name='verification'),
    webapp2.Route('/password', set_password.SetPasswordHandler),
    webapp2.Route('/login', login.LoginHandler, name='login'),
    webapp2.Route('/logout', logout.LogoutHandler, name='logout'),
    webapp2.Route('/authenticated', authenticated.AuthenticatedHandler, name='authenticated'),
    webapp2.Route('/user',user.UserHandler)
], debug=True, config=config)

logging.getLogger().setLevel(logging.DEBUG)
