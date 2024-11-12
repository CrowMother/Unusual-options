import sqlite3
from datetime import datetime, timedelta


class sqlControl():
    def __init__(self, dbFile="unusualOptions.db"):
        #create or connect to database
        self.conn = sqlite3.connect(dbFile)
        self.cursor = self.conn.cursor()

        #check if the table is over 24 hours old
        self.check_database_age()

        #create table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS stocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                expirationDate TEXT NOT NULL,
                strike TEXT NOT NULL,
                openInterst INT NOT NULL,
                lastPullTime DATE NOT NULL,
                timeCreated DATE DEFAULT CURRENT_TIMESTAMP,
                isSent INT DEFAULT 0
            )
        ''')
        self.conn.commit()

    def check_database_age(self):
        #check if the table exists 
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stocks'")
        if self.cursor.fetchone() is None:
            return
        self.cursor.execute("SELECT timeCreated FROM stocks ORDER BY timeCreated DESC LIMIT 1")
        last_pull_time = self.cursor.fetchone()[0]
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        time_diff = datetime.datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(last_pull_time, '%Y-%m-%d %H:%M:%S')
        if time_diff > timedelta(hours=24):
            self.cursor.execute("DROP TABLE stocks")


    def add_stock(self, symbol, expirationDate, strike, openInterest, lastPullTime):
        self.cursor.execute("INSERT INTO stocks (symbol, expirationDate, strike, openInterst, lastPullTime) VALUES (?, ?, ?, ?, ?)", (symbol, expirationDate, strike, openInterest, lastPullTime))
        self.conn.commit()