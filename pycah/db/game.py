from . import connection
from .user import User

class Game:
  @classmethod
  def create(cls, points_to_win, player, expansions):
    cursor = connection.cursor()
    cursor.execute('''INSERT INTO games VALUES(DEFAULT,%s) RETURNING gid''', (points_to_win,))
    gid = cursor.fetchone()[0]
    cursor.execute('''INSERT INTO game_users VALUES(%s,%s)''', (gid, player.uid))
    for expansion in expansions:
      cursor.execute('''INSERT INTO game_expansions VALUES(%s,%s)''', (gid, eid))
    connection.commit()
    return cls(gid, points_to_win)

  @classmethod
  def from_gid(cls, gid):
    cursor = connection.cursor()
    cursor.execute('''SELECT win_points FROM games WHERE gid=%s''', (gid,))
    game = cursor.fetchone()
    if game is None:
      return None # No game with that gid
    else:
      return cls(gid, game[0])

  def __init__(self, gid, points_to_win):
    self.gid = gid
    self.points_to_win = points_to_win

  def add_player(self, player):
    cursor = connection.cursor()
    cursor.execute('''INSERT INTO game_users VALUES(%s,%s)''', (self.gid, player.uid))
    connection.commit()

  def new_round(self):
    cursor = connection.cursor()
    player = None # Fix
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

  def get_players(self):
    cursor = connection.cursor()
    cursor.execute('''SELECT uid, username FROM game_players WHERE gid=%s''', (self.gid,))
    players = []
    for player in cursor:
      players.append(User(player[0], player[1]))
    connection.commit()
    return players

  @property
  def expansions(self):
    cursor = connection.cursor()
    cursor.execute('''SELECT eid FROM game_expansions WHERE gid=%s''', (self.gid,))
    eids = []
    for expansion in cursor:
      eids.append(expansion[0])
    connection.commit()
    return eids

  @property
  def started(self):
    cursor = connection.cursor()
    cursor.execute('''SELECT COUNT(*) FROM game_czar WHERE gid=%s AND round=%s''', (self.gid, 1))
    begun = cursor.fetchone()[0] == 1
    connection.commit()
    return begun
