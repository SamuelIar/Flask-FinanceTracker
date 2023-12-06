import psycopg2
from psycopg2 import sql
import os

dbParams = {
    'dbname': 'userdata',
    'user':os.getenv("USERNAME") or os.getenv("USER"),
    'password':'Password1234',
    'host':'localhost',
    'port':5432
}

def registerNewUser(username, password):
    try:
        conn = psycopg2.connect(**dbParams)
        cursor = conn.cursor()
        cursor.execute(sql.SQL("INSERT INTO users (userName, password) VALUES({username}, {password})"))
    except Exception as e:
        print("Database error: {e}")

    return

def authenticateUser(username, password):

    try:
        conn = psycopg2.connect(**dbParams)
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        stored_password = cursor.fetchone()

        if stored_password and stored_password[0] == password:
            return True
        else:
            return False
    
    except Exception as e:
        print("Database connection error: {e}")
        return False

    finally:
        cursor.close()
        conn.close()