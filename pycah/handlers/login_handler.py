import tornado.web
from ..db.user import User, current_user

class LoginHandler(tornado.web.RequestHandler):
  def _page(self, errors=False):
    self.render('login.html', handler=self, title='Login', errors=errors)
  def get(self):
    if current_user(self):
      self.redirect('/')
    else:
      self._page()
  def post(self):
    username = self.get_argument('username')
    password = self.get_argument('password')
    user = User.login(username, password)
    if user is None:
      self._page(['There is no registered user with that username.'])
    elif user == False:
      self._page(['Incorrect password.'])
    else:
      self.set_secure_cookie('uid', str(user.uid))
      self.redirect('/')

