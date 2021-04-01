import fileinput
import sys
import sqlite3

def setuptables(conn):
    cur = conn.cursor()
    
    cur.execute("CREATE TABLE IF NOT EXISTS `channels` (id integer PRIMARY KEY AUTOINCREMENT, guildid integer, channelid integer)")
    conn.commit()

    print("[SETUP] Created all tables.")