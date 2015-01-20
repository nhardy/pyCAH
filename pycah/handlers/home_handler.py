import tornado.web

class HomeHandler(tornado.web.RequestHandler):
  def get(self):
    self.render('home.html', handler=self, title='Home')
