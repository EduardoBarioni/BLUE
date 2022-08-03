import pyodbc

details = {
 'server' : 'localhost',
 'database' : 'MyDB',
 'username' : 'agvs@agvs',
 'password' : 'Eo6042539906'
 }

connect_string = 'DRIVER={{ODBC Driver 13 for SQL Server}};SERVER={server};PORT=1443; DATABASE={database};UID={username};PWD={password})'.format(**details)

connection = pyodbc.connect(connect_string)
print(connection)
