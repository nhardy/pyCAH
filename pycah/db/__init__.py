import psycopg2

try:
  c = psycopg2.connect(user='postgres', password='password')
  c.set_session(autocommit=True)
  c.cursor().execute('CREATE DATABASE pycah;')
except psycopg2.ProgrammingError:
  pass
finally:
  c.close()

connection = psycopg2.connect(database='pycah', user='postgres', password='password')
