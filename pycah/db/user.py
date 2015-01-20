from . import connection

import hashlib, random, string

def password_hash(password, salt):
  return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

def current_user(handler):
  username = handler.get_secure_cookie('username')
  if username is None:
    return None
  else:
    return User.from_username(username.decode())

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
    cursor.execute('''INSERT INTO users VALUES(DEFAULT,%s,%s,%s) RETURNING uid''', (username, password, salt))
    uid = cursor.fetchone()[0]
    connection.commit()
    return cls(uid, username)

  @classmethod
  def login(cls, username, password):
    cursor = connection.cursor()
    cursor.execute('''SELECT uid, password, salt FROM users WHERE username=%s''', (username,))
    user = cursor.fetchone()
    connection.commit()
    if user is None:
      return None # No such user exists
    else:
      if user[1] == password_hash(password, user[2]):
        return cls(user[0], username)
      else:
        return False # Wrong password

  @classmethod
  def from_username(cls, username):
    cursor = connection.cursor()
    cursor.execute('''SELECT uid FROM users WHERE username=%s''', (username,))
    user = cursor.fetchone()
    connection.commit()
    if not user:
      return None # No such user exists
    else:
      uid = user[0]
      return cls(uid, username)

  @classmethod
  def from_uid(cls, uid):
    cursor = connection.cursor()
    cursor.execute('''SELECT username FROM users WHERE uid=%s''', (uid,))
    user = cursor.fetchone()
    connection.commit()
    if not user:
      return None # No such user exists
    else:
      username = user[0]
      return cls(uid, username)

  def __init__(self, uid, username):
    self.uid = uid
    self.username = username

  def __eq__(self, other):
    if isinstance(other, User) and other.uid == self.uid:
      return True
    else:
      return False
