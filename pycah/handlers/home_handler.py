import tornado.web

from ..db.user import current_user


class HomeHandler(tornado.web.RequestHandler):
  def get(self):
    self.render('home.html', handler=self, title='Home', user=current_user(self))
