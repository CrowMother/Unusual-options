import sqlite3
from datetime import datetime, timedelta


class sqlControl():
    def __init__(self, dbFile="unusualOptions.db"):
        #create or connect to database
        self.tableCreated = False
        self.conn = sqlite3.connect(dbFile)
        self.cursor = self.conn.cursor()

        #check if the table is over 24 hours old
        self.check_database_age()

        #check if the table exists
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stocks'")
        if self.cursor.fetchone() is None:
             #create table if it doesn't exist
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS stocks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    expirationDate TEXT NOT NULL,
                    strike TEXT NOT NULL,
                    callPut TEXT NOT NULL,
                    openInterst INT NOT NULL,
                    lastPullTime DATE NOT NULL,
                    timeCreated DATE DEFAULT CURRENT_TIMESTAMP,
                    isSent INT DEFAULT 0
                )
            ''')
            self.conn.commit()
            self.tableCreated = True
        else:
            print("Table found in database")
            

       

    def check_database_age(self):
        #check if the table exists 
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stocks'")
        if self.cursor.fetchone() is None:
            return
        self.cursor.execute("SELECT timeCreated FROM stocks ORDER BY timeCreated DESC LIMIT 1")
        result = self.cursor.fetchone()
        if result is None:
            # Handle the case where no rows are found
            print("No rows found in the stocks table")
            return
        last_pull_time = result[0]
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        time_diff = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S') - datetime.strptime(last_pull_time, '%Y-%m-%d %H:%M:%S')
        if time_diff > timedelta(hours=1):
            print("Database is over 12 hours old!!!!!!!")
            self.cursor.execute("DROP TABLE stocks")
        


    def add_stock(self, symbol, expirationDate, strike, callPut, openInterest, lastPullTime):
        self.cursor.execute("INSERT INTO stocks (symbol, expirationDate, strike, callPut,openInterst, lastPullTime) VALUES (?, ?, ?, ?, ?, ?)", (symbol, expirationDate, strike, callPut, openInterest, lastPullTime))
        self.conn.commit()


    def get_max_id(self):
        self.cursor.execute("SELECT MAX(id) FROM stocks")
        return self.cursor.fetchone()[0]
    

    def get_symbol(self, id):
        #get the symbol from the database
        self.cursor.execute("SELECT symbol FROM stocks WHERE id = ?", (id,))
        return self.cursor.fetchone()[0]
    

    def get_data(self, id, column):
        #get the data from the database
        self.cursor.execute(f"SELECT {column} FROM stocks WHERE id = ?", (id,))
        return self.cursor.fetchone()[0]
    
    def set_sent(self, id):
        self.cursor.execute("UPDATE stocks SET isSent = 1 WHERE id = ?", (id,))
        self.conn.commit()