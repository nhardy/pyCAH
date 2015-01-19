from . import connection

import hashlib, random, string

def password_hash(password, salt):
  return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

class User:
  @classmethod
  def create(cls, username, password):
    cursor = connection.cursor()
    cursor.execute('''SELECT COUNT(*) FROM users WHERE username=%s''', (username,))
    exists = cursor.fetchone()[0] == 1
    if exists:
      connection.commit()
      return False # Username is already taken
    salt = ''.join([random.choice(string.printable) for _ in range(64)])
    password = password_hash(password, salt)
    cursor.execute('''INSERT INTO users VALUES(DEFAULT,%s,%s,%s)''', (username, password, salt))
    connection.commit()
    return cls(username)

  @classmethod
  def login(cls, username, password):
    cursor = connection.cursor()
    cursor.execute('''SELECT password, salt FROM users WHERE username=%s''', (username,))
    user = cursor.fetchone()
    connection.commit()
    if user is None:
      return None # No such user exists
    else:
      if user[0] == password_hash(password, user[1]):
        return cls(username)
      else:
        return False # Wrong password

  @classmethod
  def from_username(cls, username):
    cursor = connection.cursor()
    cursor.execute('''SELECT COUNT(*) FROM users WHERE username=%s''', (username,))
    exists = cursor.fetchone()[0] == 1
    connection.commit()
    if not exists:
      return None # No such user exists
    else:
      return cls(username)

  def __init__(self, username):
    self.username = username
