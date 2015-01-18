import tornado.web

class GameHandler(tornado.web.RequestHandler):
  def get(self):
    self.render('game.html', handler=self)
