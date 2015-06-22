import tornado.websocket
import json
import uuid

from ..db.game import Game
from ..db.user import current_user


class GameWebSocketHandler(tornado.websocket.WebSocketHandler):
  _GAME = Game
  sockets = {}
  games = {}
  clients = {}
  def initialize(self):
    pass
  def open(self):
    self.uuid = uuid.uuid4().hex
    self.sockets[self.uuid] = self
    self.user = current_user(self)
    if user is None:
      self.close()
  def on_message(self, message):
    print('Received', message, 'from', self)
    content = json.loads(message)
    cmd = content['cmd']
    gid = int(content['gid'])
    if cmd == 'connect':
      if gid not in self.games:
        game = self._GAME.from_gid(gid)
        if game is not None:
          self.games[gid] = game
          self.clients[gid] = set()
          self.clients[gid].add(self.uuid)
      else:
        self.clients[gid].add(self.uuid)
      self.write_message(json.dumps({'cmd': 'chat', 'message': 'PREVIOUS MESSAGES'}))
    elif self.uuid in self.clients[gid]:
      if cmd == 'chat':
        for uuid in self.clients[gid]:
          self.sockets[uuid].write_message(json.dumps({'cmd': 'chat', 'message': content['message']}))

  def on_close(self):
    print('WebSocket closed:', self)

