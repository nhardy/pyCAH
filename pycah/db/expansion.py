from . import connection

class Expansion:
  @staticmethod
  def list_all():
    cursor = connection.cursor()
    cursor.execute('''SELECT eid, name, description, (SELECT COUNT(*) FROM black_cards WHERE black_cards.eid=expansions.eid) as num_black, (SELECT COUNT(*) FROM white_cards WHERE white_cards.eid=expansions.eid) as num_white FROM expansions''')
    expansions = []
    for expansion in cursor.fetchall():
      expansions.append(Expansion(expansion[0], expansion[1], expansion[2], expansion[3], expansion[4]))
    return expansions

  @classmethod
  def from_eid(cls, eid):
    cursor = connection.cursor()
    cursor.execute('''SELECT name, description, (SELECT COUNT(*) FROM black_cards WHERE eid=%s) as num_black, (SELECT COUNT(*) FROM white_cards WHERE eid=%s) as num_white FROM expansions WHERE eid=%s''', (eid, eid, eid))
    expansion = cursor.fetchone()
    if expansion is None:
      return False # No such expansion
    else:
      return cls(eid, expansion[0], expansion[1], expansion[2], expansion[3])

  def __init__(self, eid, name, description, num_black, num_white):
    self.eid = eid
    self.name = name
    self.description = description
    self.num_black = num_black
    self.num_white = num_white
