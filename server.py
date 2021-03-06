#!/usr/bin/env python3

import tornado.ioloop
import tornado.web
import random, string

from tornado import httpserver

from pycah.handlers import HomeHandler, LoginHandler, RegisterHandler, GameHandler, LogoutHandler, GameWebSocketHandler, StaticFileHandler


def application():
  return tornado.web.Application(
                                 [
                                  (r'/', HomeHandler),
                                  (r'/login', LoginHandler),
                                  (r'/register', RegisterHandler),
                                  (r'/game(.*)', GameHandler),
                                  (r'/logout', LogoutHandler),
                                  (r'/ws', GameWebSocketHandler),
                                  (r'/styles/(.*)', StaticFileHandler, {'path': './pycah/static/styles/'}),
                                  (r'/images/(.*)', StaticFileHandler, {'path': './pycah/static/images/'}),
                                  (r'/fonts/(.*)', StaticFileHandler, {'path': './pycah/static/fonts/'}),
                                  (r'/js/(.*)', StaticFileHandler, {'path': './pycah/static/js/'}),
                                  (r'/robots.txt()', StaticFileHandler, {'path': './pycah/static/robots.txt'})
                                 ],
                                 template_path='./pycah/templates/',
                                 cookie_secret=''.join([random.choice(string.printable) for _ in range(63)]),
                                 debug=True
                                )

def main(): 
  http_server = httpserver.HTTPServer(application(), xheaders=True)
  http_server.listen(8088)
  tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
  print('Starting server...')
  main()
