#!/usr/bin/env python3

from pycah.db.user import User
from pycah.db.game import Game
from pycah.db.expansion import Expansion
from pycah.db import connection

import re, json, time

connection.set_session(autocommit=True)
cursor = connection.cursor()
cursor.execute(open('./pycah/db/create_database.sql').read())
connection.set_session(autocommit=False)

print('Importing cards...')
expansions = {}
for e in ['Base', 'CAHe1', 'CAHe2', 'CAHe3']:
  cursor.execute('''INSERT INTO expansions VALUES(DEFAULT,%s) RETURNING eid''', (e,))
  eid = cursor.fetchone()[0]
  expansions[e] = eid
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
  cards = json.loads(open('./pycah/db/cards/rest.json').read())
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
cursor.execute('''SELECT value, type FROM black_cards ORDER BY RANDOM() LIMIT 1''')
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
g = Game.create(u1, 10, Expansion.list_all())
g.add_player(u2)
g.add_player(u3)
czar, b_card = g.new_round()
print(u1.username, [c.value for c in g.get_hand(u1)])
print(u2.username, [c.value for c in g.get_hand(u2)])
print(u3.username, [c.value for c in g.get_hand(u3)])
print(czar.username, b_card.value)
for user in [u1, u2, u3]:
  if user == czar:
    continue
  hand = g.get_hand(user)
  for i in range(b_card.answers):
    g.play_card(user, hand[i])
    print(user.username, 'played', hand[i].value)
    time.sleep(0.1)
print('Round over, voting begins...' if all([g.turn_over(u) for u in [u1, u2, u3] if u != czar]) else 'A problem occurred. Round is not over for some reason.')
played_hands = g.get_played_hands()
print('Czar sees:', [[c.value for c in hand] for hand in played_hands])
print('Czar picks:', [c.value for c in played_hands[0]])
winner = g.czar_pick(played_hands[0])
print('Pick failed.' if not winner else 'Winner was {}.'.format(winner.username))

print('Done.')

User.create('nhardy', 'password')
