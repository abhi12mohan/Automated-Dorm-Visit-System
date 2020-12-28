import sqlite3
visitation_db = 'visit.db'


def create_students_table():
    conn = sqlite3.connect(visitation_db)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # make cursor into database (allows us to execute commands)
    c.execute('''CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY, fname text, lname text, kerberos text, student_id text, dorm text);''') # run a CREATE TABLE command
    conn.commit() # commit commands
    conn.close() # close connection to database

def create_connections_table():
    conn = sqlite3.connect(visitation_db)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # make cursor into database (allows us to execute commands)
    c.execute('''CREATE TABLE IF NOT EXISTS connections (id INTEGER PRIMARY KEY, friend1 INTEGER, friend2 INTEGER);''') # run a CREATE TABLE command
    conn.commit() # commit commands
    conn.close() # close connection to database

def insert_into_database(fname, lname, kerberos, student_id, dorm):
    conn = sqlite3.connect(visitation_db)
    c = conn.cursor()
    c.execute('''INSERT into students(fname, lname, kerberos, student_id, dorm) VALUES (?,?,?,?,?);''', (fname, lname, kerberos, student_id, dorm))
    conn.commit()
    conn.close()


def lookup_database():
    conn = sqlite3.connect(visitation_db)
    c = conn.cursor()
    things = c.execute('''SELECT * FROM students''').fetchall()
    for row in things:
        print(row)
    conn.commit()
    conn.close()

create_students_table()
create_connections_table()
