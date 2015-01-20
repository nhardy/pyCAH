import tornado.web
import re
from ..db.user import current_user, User

class RegisterHandler(tornado.web.RequestHandler):
  def _page(self, errors=False):
    self.render('register.html', handler=self, title='Register', errors=errors)
  def get(self):
    if current_user(self):
      self.redirect('/')
    else:
      self._page()
  def post(self):
    username = self.get_argument('username')
    password = self.get_argument('password')
    confirm = self.get_argument('confirm')
    errors = []
    if not re.search(r'^[a-z0-9][a-z0-9_.-]{3,28}[a-z0-9]$', username) or re.search(r'[_.-]{2}', username):
      errors.append('That username is invalid.')
    elif User.from_username(username) is not None:
      errors.append('That username is already taken.')
    if password != confirm:
      errors.append('Entered passwords do not match.')
    elif not (8 <= len(password) <= 64):
      errors.append('Your password does not meet the length requirements. It must be between 8 and 64 characters.')
    if len(errors) > 0:
      self._page(errors)
    else:
      user = User.create(username, password)
      self.set_secure_cookie('uid', str(user.uid))
      self.redirect('/')
