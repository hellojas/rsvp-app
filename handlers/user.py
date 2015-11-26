from base import BaseHandler
from base import user_required
import logging
import json
from webapp2_extras.appengine.auth.models import UserToken
from webapp2_extras.appengine.auth.models import User
from google.appengine.ext import ndb

class UserHandler(BaseHandler):
  @user_required
  def post(self):
    logging.info(self.user_info)
    id = self.user_info["user_id"]
    datuser = User.get_by_id(id)

    curuser = {
    "first":datuser.name,
    "last": datuser.last_name,
    "username": datuser.auth_ids[0],
    "email": datuser.email
    }
    self.response.write(json.dumps(curuser))

    

