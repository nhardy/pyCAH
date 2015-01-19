from . import connection

connection.set_session(autocommit=True)
cursor = connection.cursor()
cursor.execute(open('create_database.sql').read())
cursor.close()
connection.close()
