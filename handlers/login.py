from base import BaseHandler
import json
import logging
from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError
from webapp2_extras.appengine.auth.models import UserToken

class LoginHandler(BaseHandler):
  def get(self):
    self.render_template('login.html')

  def post(self):
    data = self.request.body
    info = json.loads(data)
    
    try:
      u = self.auth.get_user_by_password(info["username"], info["password"], remember=True,
        save_session=True)
      logging.info(u)
      self.response.out.write("All Good!")
    except (InvalidAuthIdError, InvalidPasswordError) as e:
      logging.info('Login failed for user %s because of %s', info["username"], type(e))
      self.response.out.write("Failure")


