import tornado.ioloop
import tornado.web

from pycah.handlers import *

def application():
  return tornado.web.Application(
                                 [
                                  (r'/', HomeHandler),
                                  (r'/login', LoginHandler),
                                  (r'/register', RegisterHandler),
                                  (r'/game', GameHandler),
                                  # Additional Handlers here
                                  (r'/styles/(.*)', StaticFileHandler, {'path': './pycah/static/styles/'}),
                                  (r'/images/(.*)', StaticFileHandler, {'path': './pycah/static/images/'}),
                                  (r'/fonts/(.*)', StaticFileHandler, {'path': './pycah/static/fonts/'}),
                                  (r'/js/(.*)', StaticFileHandler, {'path': './pycah/static/js/'}),
                                  (r'/robots.txt()', StaticFileHandler, {'path': './pycah/static/robots.txt'})
                                 ],
                                 template_path='./pycah/templates/'
                                )

def main():
  application().listen(80)
  tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
  print('Starting server...')
  main()
