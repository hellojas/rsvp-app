from base import BaseHandler
from base import user_required

class AuthenticatedHandler(BaseHandler):
  @user_required
  def get(self):
    self.render_template('home.html')