import psycopg2

c = psycopg2.connect(user='postgres', password='password')
c.set_session(autocommit=True)
cur = c.cursor()
try:
  cur.execute('CREATE DATABASE pycah;')
  c.commit()
  c.close()
  c = psycopg2.connect(database='pycah', user='postgres', password='password')
  c.set_session(autocommit=True)
  cur = c.cursor()
  cur.execute(open('./pycah/db/create_database.sql').read())
  c.commit()
  c.close() 
except psycopg2.ProgrammingError:
  c.close() 

connection = psycopg2.connect(database='pycah', user='postgres', password='password')
