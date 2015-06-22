import tornado.websocket
import json
import uuid
import html

from ..db.game import Game
from ..db.user import current_user


class GameWebSocketHandler(tornado.websocket.WebSocketHandler):
  _GAME = Game
  sockets = {}
  games = {}
  clients = {}

  def _write_all(self, message):
    for ws_uuid in self.clients[self.gid]:
      self.sockets[ws_uuid].write_message(message)
  def _update_players(self):
    self._write_all(json.dumps({'cmd': 'players', 'players': list(sorted(set([self.sockets[ws_uuid].user.username for ws_uuid in self.clients[self.gid]])))}))
  def initialize(self):
    pass
  def open(self):
    self.uuid = uuid.uuid4().hex
    self.sockets[self.uuid] = self
    self.user = current_user(self)
    if self.user is None:
      self.close()
  def on_message(self, message):
    content = json.loads(message)
    cmd = content['cmd']
    if cmd == 'connect':
      gid = content['gid']
      if gid not in self.games:
        game = self._GAME.from_gid(gid)
        if game is not None:
          self.gid = gid
          self.games[self.gid] = game
          self.clients[self.gid] = set()
          self.clients[self.gid].add(self.uuid)
      else:
        self.gid = gid
        self.clients[self.gid].add(self.uuid)
      self._update_players()
      self.write_message(json.dumps({'cmd': 'chat', 'sender': '[SYSTEM]', 'message': 'Successfully joined.'}))
    elif self.uuid in self.clients[self.gid]:
      if cmd == 'chat' and len(content['message']) > 0:
        self._write_all(json.dumps({'cmd': 'chat', 'sender': self.user.username, 'message': html.escape(content['message'])}))

  def _cleanup(self):
    self.clients[self.gid].remove(self.uuid)
  def on_close(self):
    self._cleanup()
    self._update_players()
  def on_finish(self):
    self._cleanup()
    self._update_players()

