from pycah.db.user import User
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
  print('Finished importing')
except Exception as e:
  print('Failed to import')
  raise e

cursor.execute('''SELECT value, type FROM black_cards WHERE eid=%s AND cid>=(SELECT COUNT(*) FROM black_cards WHERE eid=%s)*RANDOM() ORDER BY cid LIMIT 1''', (eid, eid))
black_card = cursor.fetchone()
connection.commit()
print(black_card[0])
cursor.execute('''SELECT value FROM white_cards WHERE eid=%s AND cid>=(SELECT COUNT(*) FROM white_cards WHERE eid=%s)*RANDOM() ORDER BY cid LIMIT %s''', (eid, eid, black_card[1]))
white_cards = cursor.fetchall()
for c in white_cards:
  print(c[0])
