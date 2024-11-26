import sqlite3
from datetime import datetime, timedelta



class sqlControlMainTable():
    def __init__(self, dbFile="unusualOptions.db"):
        #create or connect to database
        self.tableCreated = False
        self.conn = sqlite3.connect(dbFile)
        self.cursor = self.conn.cursor()

        #drop all tables
        # self.cursor.execute("DROP TABLE IF EXISTS stocks")
        # self.cursor.execute("DROP TABLE IF EXISTS unique_stocks")
        # self.conn.commit()


        #check if the table is over 24 hours old
        # self.check_database_age()

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

        # Check if the `unique_stocks` table exists; if not, create it
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='unique_stocks'")
        if self.cursor.fetchone() is None:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS unique_stocks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT UNIQUE NOT NULL
                )
            ''')
            self.conn.commit()
            print("Created the unique_stocks table.")
        else:
            print("Unique stocks table found in database.")
            

       

    def check_database_age(self):
    # Check if the `stocks` table exists
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stocks'")
        if self.cursor.fetchone() is None:
            return
        
        # Get the most recent `timeCreated` value from the `stocks` table
        self.cursor.execute("SELECT timeCreated FROM stocks ORDER BY timeCreated DESC LIMIT 1")
        result = self.cursor.fetchone()
        
        if result is None:
            # Handle the case where no rows are found
            print("No rows found in the stocks table")
            return
        
        last_pull_time = datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S')
        current_time = datetime.now()
        
        time_diff = current_time - last_pull_time
        print("Time difference:", time_diff)
        self.conn.commit()
        # Check if the time difference exceeds 12 hours (or 5 minutes for testing)
        if time_diff > timedelta(hours=72):  # Use `minutes=5` if testing shorter timeframes
            print("Database is over 12 hours old!!!!!!!")
            # Delete the stocks table
            self.cursor.execute("DROP TABLE stocks")
            self.conn.commit()
        

    def get_strikes(self,symbol, expirationDate, callPut):
        self.cursor.execute("SELECT strike FROM stocks WHERE symbol LIKE ? AND expirationDate LIKE ? AND callPut = ?", ('%' + symbol + '%', '%' + expirationDate + '%', callPut))
        #convert to doubles from strings
        # return [float(row[0]) for row in self.cursor.fetchall()]
        return [float(row[0]) for row in self.cursor.fetchall()]



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


    def add_unique_stock(self, symbol):
        try:
            self.cursor.execute("INSERT OR IGNORE INTO unique_stocks (symbol) VALUES (?)", (symbol,))
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            print(f"Failed to insert {symbol}: {e}")

    def get_all_unique_stocks(self):
        self.cursor.execute("SELECT symbol FROM unique_stocks")
        return [row[0] for row in self.cursor.fetchall()]        
    
    def get_unique_stock(self, symbol):
        self.cursor.execute("SELECT symbol FROM unique_stocks WHERE symbol = ?", (symbol,))
        return self.cursor.fetchone()
    
    def get_last_unique_stock(self):
        self.cursor.execute("SELECT symbol FROM unique_stocks ORDER BY symbol DESC LIMIT 1")
        return self.cursor.fetchone()