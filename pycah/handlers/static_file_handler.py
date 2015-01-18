import tornado.web

import mimetypes

class StaticFileHandler(tornado.web.StaticFileHandler):
  def get_content_type(self):
    mime, encoding = mimetypes.guess_type(self.absolute_path)
    if mime is not None:
      return mime
    elif self.absolute_path.endswith('.ttf'):
      return 'application/x-font-ttf'
    elif self.absolute_path.endswith('.woff'):
      return 'application/font-woff'
    elif self.absolute_path.endswith('.7z'):
      return 'application/x-7z-compressed'
    else:
      return 'application/octet-stream'
