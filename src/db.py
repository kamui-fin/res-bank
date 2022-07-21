import sqlite3

class Database:
    def __init__(self, path):
        self.conn = sqlite3.connect("data.db")
        self.cur = self.conn.cursor()
        self.initialize_tables()
    
    def initialize_tables(self):
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                author INTEGER NOT NULL,
                created_on DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
            )
        ''')

    def get_submissions(self):
        self.cur.execute("SELECT * FROM submissions")
        return self.cur.fetchall()
    
    def insert_submission(self, keyword, url, author):
        self.cur.execute("INSERT INTO submissions (keyword, url, author) VALUES (?, ?, ?)", (keyword, url, author))
        self.conn.commit()
    
    def remove_submission(self, url):
        self.cur.execute("DELETE FROM submissions WHERE url = ?", (url))
        self.conn.commit()
