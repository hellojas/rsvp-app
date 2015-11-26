from base import BaseHandler
import logging

class VerificationHandler(BaseHandler):
  def get(self, *args, **kwargs):
    logging.info("Request Handler Reached")
    user = None
    user_id = kwargs['user_id']
    logging.info(user_id)
    signup_token = kwargs['signup_token']
    logging.info(signup_token)
    verification_type = kwargs['type']
    logging.info(verification_type)

    # it should be something more concise like
    # self.auth.get_user_by_token(user_id, signup_token
    # unfortunately the auth interface does not (yet) allow to manipulate
    # signup tokens concisely
    user, ts = self.user_model.get_by_auth_token(int(user_id), signup_token,
      'signup')
    logging.info(user)
    logging.info(ts)


    if not user:
      logging.info('Could not find any user with id "%s" signup token "%s"',
        user_id, signup_token)
      self.abort(404)
    
    # store user data in the session
    logging.info("Dict creation")
    userdict = self.auth.store.user_to_dict(user)
    logging.info(userdict)
    logging.info("Set Session")
    self.auth.set_session(userdict, remember=True)

    if verification_type == 'v':
      logging.info("verification type v")
      # remove signup token, we don't want users to come back with an old link
      self.user_model.delete_signup_token(user.get_id(), signup_token)

      if not user.verified:
        user.verified = True
        user.put()

      self.render_template('home.html')
      return
    elif verification_type == 'p':
      logging.info("verification type p")
      # supply user to the page
      params = {
        'user': user,
        'token': signup_token
      }
      self.render_template('resetpassword.html', params)
    else:
      logging.info('verification type not supported')
      self.abort(404)