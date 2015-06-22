from . import connection
from .user import User
from .cards import BlackCard, WhiteCard
from .expansion import Expansion

class Game:
  @classmethod
  def create(cls, creator, points_to_win, expansions):
    cursor = connection.cursor()
    cursor.execute('''INSERT INTO games VALUES(DEFAULT,%s,%s) RETURNING gid''', (creator.uid, points_to_win))
    gid = cursor.fetchone()[0]
    cursor.execute('''INSERT INTO game_users VALUES(%s,%s)''', (gid, creator.uid))
    for expansion in expansions:
      cursor.execute('''INSERT INTO game_expansions VALUES(%s,%s)''', (gid, expansion.eid))
    connection.commit()
    return cls(gid, creator, points_to_win)

  @classmethod
  def from_gid(cls, gid):
    cursor = connection.cursor()
    cursor.execute('''SELECT uid, win_points FROM games WHERE gid=%s''', (gid,))
    game = cursor.fetchone()
    if game is None:
      return None # No game with that gid
    else:
      return cls(gid, User.from_uid(game[0]), game[1])

  def __init__(self, gid, creator, points_to_win):
    self.gid = gid
    self.creator = creator
    self.points_to_win = points_to_win

  def add_player(self, player):
    cursor = connection.cursor()
    cursor.execute('''INSERT INTO game_users VALUES(%s,%s)''', (self.gid, player.uid))
    connection.commit()

  def new_round(self):
    cursor = connection.cursor()
    player = self.get_random_player() # Change to proper ordering later
    cursor.execute('''
                   SELECT black_cards.eid, black_cards.cid
                   FROM game_expansions
                   INNER JOIN black_cards ON game_expansions.eid=black_cards.eid
                   LEFT JOIN game_czar ON black_cards.eid=game_czar.eid AND black_cards.cid=game_czar.cid
                   WHERE game_czar.cid IS NULL
                   ORDER BY RANDOM()
                   LIMIT 1
                   ''')
    black_card = cursor.fetchone()
    connection.commit()
    eid = black_card[0]
    cid = black_card[1]
    cursor.execute('''INSERT INTO game_czar VALUES(%s,DEFAULT,%s,%s,%s,NULL)''', (self.gid, player.uid, eid, cid))
    connection.commit()
    card = BlackCard(eid, cid)
    for p in self.get_players():
      self.fill_hand(p, 10 + card.draw)
    return (player, card)

  def fill_hand(self, player, amount=10):
    cursor = connection.cursor()
    cursor.execute('''
                   SELECT white_cards.eid, white_cards.cid
                   FROM game_expansions
                   INNER JOIN white_cards ON game_expansions.eid=white_cards.eid
                   LEFT JOIN game_cards ON white_cards.eid=game_cards.eid AND white_cards.cid=game_cards.cid
                   WHERE game_cards.cid IS NULL
                   ORDER BY RANDOM()
                   LIMIT (%s-(SELECT COUNT(*) FROM game_cards WHERE gid=%s AND uid=%s AND used=%s))
                   ''', (amount, self.gid, player.uid, False))
    for card in cursor.fetchall():
      cursor.execute('''INSERT INTO game_cards VALUES(%s,%s,%s,%s,%s)''', (self.gid, player.uid, card[0], card[1], False))
    connection.commit()

  def get_players(self):
    cursor = connection.cursor()
    cursor.execute('''SELECT game_users.uid, users.username FROM game_users LEFT JOIN users on game_users.uid=users.uid WHERE gid=%s''', (self.gid,))
    players = []
    for player in cursor.fetchall():
      players.append(User(player[0], player[1]))
    connection.commit()
    return players

  def get_num_players(self):
    cursor = connection.cursor()
    cursor.execute('''SELECT COUNT(*) FROM game_users WHERE gid=%s''', (self.gid,))
    players = cursor.fetchone()[0]
    connection.commit()
    return players

  def get_random_player(self):
    cursor = connection.cursor()
    cursor.execute('''SELECT game_users.uid, users.username FROM game_users LEFT JOIN users on game_users.uid=users.uid WHERE gid=%s ORDER BY RANDOM() LIMIT 1''', (self.gid,))
    player = cursor.fetchone()
    player = User(player[0], player[1])
    connection.commit()
    return player

  def is_in(self, player):
    cursor = connection.cursor()
    cursor.execute('''SELECT COUNT(*) FROM game_users WHERE gid=%s AND uid=%s''', (self.gid, player.uid))
    if cursor.fetchone()[0] == 0:
      connection.commit()
      return False
    else:
      connection.commit()
      return True

  def get_hand(self, player):
    cursor = connection.cursor()
    cursor.execute('''SELECT eid, cid FROM game_cards WHERE gid=%s AND uid=%s AND used=%s''', (self.gid, player.uid, False))
    cards = []
    for card in cursor.fetchall():
      cards.append(WhiteCard(card[0], card[1]))
    connection.commit()
    return cards

  def get_czar(self):
    cursor = connection.cursor()
    cursor.execute('''SELECT game_czar.czar_id, users.username FROM game_czar LEFT JOIN users ON game_czar.czar_id=users.uid WHERE gid=%s and round=(SELECT MAX(round) FROM game_czar WHERE gid=%s)''', (self.gid, self.gid))
    czar = cursor.fetchone()
    connection.commit()
    return User(czar[0], czar[1])

  def get_black_card(self):
    cursor = connection.cursor()
    cursor.execute('''SELECT eid, cid FROM game_czar WHERE gid=%s AND round=(SELECT MAX(round) FROM game_czar WHERE gid=%s)''', (self.gid, self.gid))
    card = cursor.fetchone()
    card = BlackCard(card[0], card[1])
    connection.commit()
    return card

  def play_card(self, player, card):
    if player == self.get_czar():
      return False # Czar may not play cards
    cursor = connection.cursor()
    cursor.execute('''
                   UPDATE game_cards SET used=%s
                   WHERE
                     gid=%s AND uid=%s AND eid=%s AND cid=%s
                     AND
                       (
                        SELECT COUNT(*) FROM game_moves
                        WHERE gid=%s AND uid=%s
                          AND round=(SELECT MAX(round) FROM game_czar WHERE gid=%s)
                       ) < %s
                   RETURNING %s''',
                   (True, self.gid, player.uid, card.eid, card.cid, self.gid, player.uid, self.gid, self.get_black_card().answers, True))
    can_play = cursor.fetchone()
    if can_play is None:
      connection.commit()
      return False # Player did not have this card or had already played enough cards
    else:
      cursor.execute('''INSERT INTO game_moves VALUES(%s,(SELECT MAX(round) FROM game_czar WHERE gid=%s),%s,%s,%s,NOW())''', (self.gid, self.gid, player.uid, card.eid, card.cid))
      connection.commit()
      return True # Play was successful

  @property
  def expansions(self):
    cursor = connection.cursor()
    cursor.execute('''SELECT eid FROM game_expansions WHERE gid=%s''', (self.gid,))
    expansions_list = []
    for e in cursor.fetchall():
      expansions_list.append(Expansion.from_eid(e[0]))
    connection.commit()
    return expansions_list

  @property
  def started(self):
    cursor = connection.cursor()
    cursor.execute('''SELECT COUNT(*) FROM game_czar WHERE gid=%s AND round=%s''', (self.gid, 1))
    begun = cursor.fetchone()[0] == 1
    connection.commit()
    return begun

  def turn_over(self, player):
    cursor = connection.cursor()
    cursor.execute('''SELECT %s-COUNT(*) FROM game_moves WHERE gid=%s AND round=(SELECT MAX(round) FROM game_czar WHERE gid=%s) AND uid=%s''', (self.get_black_card().answers, self.gid, self.gid, player.uid))
    over = cursor.fetchone()[0] == 0
    connection.commit()
    return over

  def get_played_hands(self):
    cursor = connection.cursor()
    cursor.execute('''SELECT eid, cid, uid FROM game_moves WHERE gid=%s AND round=(SELECT MAX(round) FROM game_czar WHERE gid=%s)''', (self.gid, self.gid))
    hands = {}
    for card in cursor.fetchall():
      eid, cid, uid = card
      if uid not in hands:
        hands[uid] = []
      hands[uid].append(WhiteCard(eid, cid))
    connection.commit()
    return list(hands.values())
