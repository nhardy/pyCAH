from . import connection

class BlackCard:
  def __init__(self, eid, cid): # Should only be invoked after successful database query
    self.eid = eid
    self.cid = cid
  @property
  def value(self):
    cursor = connection.cursor()
    cursor.execute('''SELECT value FROM black_cards WHERE eid=%s AND cid=%s''', (self.eid, self.cid))
    val = cursor.fetchone()[0]
    connection.commit()
    return val
  @property
  def answers(self):
    cursor = connection.cursor()
    cursor.execute('''SELECT type FROM black_cards WHERE eid=%s AND cid=%s''', (self.eid, self.cid))
    t = cursor.fetchone()[0]
    connection.commit()
    return t
  @property
  def draw(self):
    return 2 if self.answers == 3 else 0

class WhiteCard:
  def __init__(self, eid, cid): # Should only be invoked after successful database query
    self.eid = eid
    self.cid = cid
  @property
  def value(self):
    cursor = connection.cursor()
    cursor.execute('''SELECT value FROM white_cards WHERE eid=%s AND cid=%s''', (self.eid, self.cid))
    val = cursor.fetchone()[0]
    connection.commit()
    return val
  @property
  def trump(self):
    cursor = connection.cursor()
    cursor.execute('''SELECT trump FROM white_cards WHERE eid=%s AND cid=%s''', (self.eid, self.cid))
    trump = cursor.fetchone()[0]
    connection.commit()
    return trump
