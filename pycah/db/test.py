import psycopg2

connection = psycopg2.connect(database='pycah', user='postgres', password='password')
connection.set_session(autocommit=True)
cursor = connection.cursor()
cursor.execute(open('create_database.sql').read())
cursor.close()
connection.close()
