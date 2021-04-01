import fileinput
import sys
import sqlite3

def setuptables(conn):
    cur = conn.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS `channels` (guildid integer PRIMARY KEY, channelid integer, webhookurl text)")
    conn.commit()

    print("[SETUP] Created all tables.")