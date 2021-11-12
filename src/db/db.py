import sqlite3

def connect(location):
    conn = sqlite3.connect(location)
    conn.row_factory = sqlite3.Row

    return conn