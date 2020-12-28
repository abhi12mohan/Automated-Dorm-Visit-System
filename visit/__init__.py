import os
from flask import Flask, render_template, request, session, url_for, redirect, flash, jsonify
from datetime import datetime, timedelta
from functools import wraps
import sqlite3
import os.path
from Crypto.Cipher import AES

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
visitation_db = os.path.join(BASE_DIR, "visit.db")



app = Flask(__name__)
app.secret_key = 'blah'



def insert_into_database(fname, lname, kerberos, student_id, dorm):
    conn = sqlite3.connect(visitation_db)
    c = conn.cursor()
    c.execute('''INSERT into students(fname, lname, kerberos, student_id, dorm) VALUES (?,?,?,?,?);''', (fname, lname, kerberos, student_id, dorm))
    conn.commit()
    conn.close()

def insert_into_connections(student1, student2):
    conn = sqlite3.connect(visitation_db)
    c = conn.cursor()
    c.execute('''INSERT into connections(friend1, friend2) VALUES (?, ?);''', (student1, student2))
    conn.commit()
    conn.close()



def lookup_database(arr):
    conn = sqlite3.connect(visitation_db)
    c = conn.cursor()
    things = c.execute('''SELECT * FROM students''').fetchall()
    for row in things:
        arr.append(row)
    conn.commit()
    conn.close()

def lookup_connections(arr):
    conn = sqlite3.connect(visitation_db)
    c = conn.cursor()
    things = c.execute('''SELECT * FROM connections''').fetchall()
    for row in things:
        arr.append(row)
    conn.commit()
    conn.close()

def check_login(kerb):
    conn = sqlite3.connect(visitation_db)
    c = conn.cursor()
    user = c.execute('''SELECT * FROM students WHERE kerberos = ?''', (kerb, )).fetchone()
    conn.commit()
    conn.close()
    return user
def fetch_user_by_sid(studentID):
    conn = sqlite3.connect(visitation_db)
    c = conn.cursor()
    n_studentID = int(studentID)
    user = c.execute('''SELECT * from students WHERE student_id = ?''', (n_studentID, )).fetchone()
    print(user)
    conn.commit()
    conn.close()
    return user

def fetch_user_by_kerb(kerb):
    conn = sqlite3.connect(visitation_db)
    c = conn.cursor()
    user = c.execute('''SELECT * FROM students WHERE kerberos = ?''', (kerb, )).fetchone()
    conn.commit()
    conn.close()
    return user
def fetch_user_by_id(id):
    conn = sqlite3.connect(visitation_db)
    c = conn.cursor()
    user = c.execute('''SELECT * FROM students WHERE id = ?''', (id, )).fetchone()
    conn.commit()
    conn.close()
    return user
def get_conns_of_user(id, conn_list):
    conn = sqlite3.connect(visitation_db)
    c = conn.cursor()
    conns = c.execute('''SELECT * FROM connections WHERE friend2 = ?''', (id, )).fetchall()
    for c in conns:
        conn_list.append(c)
    conn.commit()
    conn.close()

def get_guests_of_user(kerberos, guest_list):
    conn = sqlite3.connect(visitation_db)
    c = conn.cursor()
    user = c.execute('''SELECT * FROM students WHERE kerberos = ?''', (kerberos, )).fetchone()
    id = user[0]
    conns = c.execute('''SELECT * FROM connections WHERE friend1 = ?''', (id, )).fetchall()
    for c in conns:
        id_of_guest = c[2]
        new_user = fetch_user_by_id(id_of_guest)
        guest_list.append( {new_user[0]: str(new_user[1]) + " " + str(new_user[2])} )
    conn.commit()
    conn.close()


def remove_a_guest(your_id, guest_id):
    conn = sqlite3.connect(visitation_db)
    c = conn.cursor()
    c.execute('''DELETE FROM connections WHERE friend1 = ? AND friend2 = ?''', (your_id, guest_id))
    conn.commit()
    conn.close()




def update_dorm_info(kerb, dorm):
    conn = sqlite3.connect(visitation_db)
    c = conn.cursor()
    conns = c.execute('''UPDATE students SET dorm = ? WHERE kerberos = ?; ''', (dorm, kerb))
    conn.commit()
    conn.close()


def insert_into_attempts(student_id, student_fname, student_lname, student_kerb):
    logged_time = datetime.now()
    conn = sqlite3.connect(visitation_db)
    c = conn.cursor()
    c.execute('''INSERT into attempts(student_id, student_fname, student_lname, logged_time, student_kerb) VALUES (?, ?, ?, ?, ?);''', (student_id, student_fname, student_lname, logged_time, student_kerb))
    conn.commit()
    conn.close()


def get_all_attempts(arr):
    conn = sqlite3.connect(visitation_db)
    c = conn.cursor()
    things = c.execute('''SELECT * FROM attempts ORDER BY logged_time DESC''').fetchall()

    for row in things:
        arr.append(row)
    conn.commit()
    conn.close()






def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return render_template('login.html')
    return wrap


import visit.views
