from base import BaseHandler
import logging
import json

class SignupHandler(BaseHandler):
  def get(self):
    self.render_template('signup.html')


  def post(self):
    data = self.request.body
    logging.info(data)
    info = json.loads(data)
   

    user_name = str(info["username"])
    logging.info(user_name)
    email = str(info["email"])
    logging.info(email)
    first_name = str(info["first"])
    logging.info(first_name)
    password = str(info["password"])
    logging.info(password)
    last_name = str(info["last"])
    logging.info(last_name)

    unique_properties = ['email']
    user_data = self.user_model.create_user(
      user_name,
      unique_properties,
      email=email, 
      name=first_name, 
      password_raw=password,
      last_name=last_name, 
      verified=False)
    if not user_data[0]: #user_data is a tuple
      logging.info(user_data)
      logging.info(user_data[0])
      logging.info(user_data[1])
      self.response.out.write("Failure")
    else:
      logging.info(user_data)
      logging.info(user_data[0])
      logging.info(user_data[1])
      user = user_data[1]
      logging.info(user)

      user_id = user.get_id()

      token = self.user_model.create_signup_token(user_id)

      verification_url = self.uri_for('verification', type='v', user_id=user_id, signup_token=token, _full=True)

      self.response.out.write(verification_url)