from pycah.db.user import User
from pycah.db.game import Game
from pycah.db import connection

import re

connection.set_session(autocommit=True)
cursor = connection.cursor()
cursor.execute(open('./pycah/db/create_database.sql').read())
connection.set_session(autocommit=False)

try:
  print('Importing Australian Edition cards...')
  regex = re.compile(r'_+')
  cursor.execute('''INSERT INTO expansions VALUES(DEFAULT,%s,%s) RETURNING eid''', ('Australian Edition', 'The Australian Edition of Cards against Humanity.'))
  eid = cursor.fetchone()[0]
  with open('./pycah/db/cards/black_aus.txt', encoding='utf-8') as f:
    for l in f:
      line = l.strip()
      line = regex.sub('_', line)
      spaces = max(1, line.count('_'))
      cursor.execute('''INSERT INTO black_cards VALUES(%s,DEFAULT,%s,%s)''', (eid, spaces, line))
  with open('./pycah/db/cards/white_aus.txt', encoding='utf-8') as f:
    for l in f:
      line = l.strip()
      cursor.execute('''INSERT INTO white_cards VALUES(%s,DEFAULT,%s,%s)''', (eid, False, line))
  connection.commit()
  print('Finished importing Australian Edition')
except Exception as e:
  print('Failed to import Australian Edition')
  raise e

try:
  print('Importing the rest...')
  cards = eval(open('./pycah/db/cards/rest.json').read())
  expansions = {}
  for card in cards:
    if card['expansion'] not in expansions:
      cursor.execute('''INSERT INTO expansions VALUES(DEFAULT,%s) RETURNING eid''', (card['expansion'],))
      expansions[card['expansion']] = cursor.fetchone()[0]
    if card['numAnswers'] == 0:
      cursor.execute('''INSERT INTO white_cards VALUES(%s,DEFAULT,%s,%s)''', (expansions[card['expansion']], False, card['text']))
    else:
      cursor.execute('''INSERT INTO black_cards VALUES(%s,DEFAULT,%s,%s)''', (expansions[card['expansion']], card['numAnswers'], card['text']))
  connection.commit()
  print('Finished importing the rest')
except Exception as e:
  print('Failed to import the rest')
  raise e

print('Testing random cards: ')
cursor.execute('''SELECT value, type FROM black_cards black_cards ORDER BY RANDOM() LIMIT 1''')
black_card = cursor.fetchone()
connection.commit()
print(black_card[0])
cursor.execute('''SELECT value FROM white_cards ORDER BY RANDOM() LIMIT %s''', (black_card[1],))
white_cards = cursor.fetchall()
for c in white_cards:
  print(c[0])
print('Test complete.')

print('Game test...')
u1 = User.create('user1', 'password')
u2 = User.create('user2', 'password')
u3 = User.create('user3', 'password')
g = Game.create(10, u1, [1,2,3,4])
g.add_player(u2)
g.add_player(u3)
czar, b_card = g.new_round()
print([c.value for c in g.get_hand(u1)])
print([c.value for c in g.get_hand(u2)])
print([c.value for c in g.get_hand(u3)])
print(czar.username, b_card.value)
print('Done.')
