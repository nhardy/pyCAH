import tornado.websocket
import json
import uuid
import html

from ..db.game import Game
from ..db.cards import WhiteCard
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
    if self.gid in self.clients and self.user is not None:
      self._write_all(json.dumps({'cmd': 'players', 'players': list(sorted(set([self.sockets[ws_uuid].user.username for ws_uuid in self.clients[self.gid]])))}))
  def _round(self, ws, czar, black_card):
    ws.write_message(json.dumps({'cmd': 'chat', 'sender': '[SYSTEM', 'message': ('You are the card czar.' if ws.user == czar else '{} is the card czar.'.format(czar.username))}))
    msg = {
      'cmd': 'new_round',
      'czar': czar.username,
      'eid': black_card.eid,
      'cid': black_card.cid,
      'value': black_card.value,
      'hand': [{'eid': card.eid, 'cid': card.cid, 'value': card.value, 'trump': card.trump} for card in self.games[self.gid].get_hand(ws.user)]
    }
    ws.write_message(json.dumps(msg))
  def initialize(self):
    pass
  def open(self):
    self.uuid = uuid.uuid4().hex
    self.sockets[self.uuid] = self
    self.user = current_user(self)
    self.gid = None
    if self.user is None:
      self.close()
  def on_message(self, message):
    if self.user is None:
      self.close()
      return
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
      self._write_all(json.dumps({'cmd': 'chat', 'sender': '[SYSTEM]', 'message': '{} joined the chat.'.format(self.user.username)}))
      if self.games[self.gid].started and self.games[self.gid].is_in(self.user):
        self._write_all(json.dumps({'cmd': 'chat', 'sender': '[SYSTEM]', 'message': '{} joined the game.'.format(self.user.username)}))
        czar = self.games[self.gid].get_czar()
        self._round(self, czar, self.games[self.gid].get_black_card())
      else:
        if self.user == self.games[self.gid].creator:
          self.write_message(json.dumps({'cmd': 'chat', 'sender': '[SYSTEM]', 'message': 'To start the game when ready, type /start'}))
    elif self.uuid in self.clients[self.gid]:
      if cmd == 'chat':
        msg = content['message']
        if len(msg) == 0:
          return
        elif msg[0] == '/':
          if msg == '/start' and self.user == self.games[self.gid].creator and not self.games[self.gid].started and self.games[self.gid].get_num_players() > 2:
            self._write_all(json.dumps({'cmd': 'chat', 'sender': '[SYSTEM]', 'message': 'Game starting...'}))
            czar, black_card = self.games[self.gid].new_round()
            for ws_uuid in self.clients[self.gid]:
              ws = self.sockets[ws_uuid]
              if not self.games[self.gid].is_in(ws.user):
                continue
              self._round(ws, czar, black_card)
        else:
          self._write_all(json.dumps({'cmd': 'chat', 'sender': self.user.username, 'message': html.escape(content['message'])}))
      elif cmd == 'join':
        self.games[self.gid].add_player(self.user)
        self._write_all(json.dumps({'cmd': 'chat', 'sender': '[SYSTEM]', 'message': '{} joined the game.'.format(self.user.username)}))
        if self.games[self.gid].started:
          self._round(self, self.games[self.gid].get_czar(), self.games[self.gid].get_black_card())
      elif cmd == 'white_card':
        self.games[self.gid].play_card(self.user, WhiteCard(int(content["eid"]), int(content["cid"])))
        if all([self.games[self.gid].turn_over(self.sockets[ws_uuid].user) for ws_uuid in self.clients[self.gid] if self.games[self.gid].is_in(self.sockets[ws_uuid].user) and self.sockets[ws_uuid].user != self.games[self.gid].get_czar()]):
          czar_ws = [self.sockets[ws_uuid] for ws_uuid in self.clients[self.gid] if self.sockets[ws_uuid].user == self.games[self.gid].get_czar()][0]
          msg = {
            'cmd': 'vote_required',
            'hands': [[{'eid': card.eid, 'cid': card.cid, 'value': card.value, 'trump': card.trump} for card in hand] for hand in self.games[self.gid].get_played_hands()]
          }
          czar_ws.write_message(json.dumps(msg))
      elif cmd == 'vote':
        if self.user == self.games[self.gid].get_czar():
          hand = [WhiteCard(c['eid'], c['cid']) for c in content['hand']]
          self.games[self.gid].czar_pick(hand)
        

  def _cleanup(self):
    if self.gid in self.clients:
      self.clients[self.gid].remove(self.uuid)
  def on_close(self):
    self._cleanup()
    self._update_players()
  def on_finish(self):
    self._cleanup()
    self._update_players()

