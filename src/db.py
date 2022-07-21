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
                keywords TEXT NOT NULL,
                description TEXT,
                meta_title TEXT,
                meta_description TEXT,
                url TEXT NOT NULL UNIQUE,
                author INTEGER NOT NULL,
                created_on DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
            )
        ''')

    def get_submissions(self):
        self.cur.execute("SELECT * FROM submissions")
        return self.cur.fetchall()

    def get_submissions_by_query(self, query, user_id, limit):
        sql = """SELECT * FROM submissions WHERE 1"""
        params = {}
        if query:
            sql += " AND submissions MATCH :query"
            params["query"] = query
        if user_id:
            sql += " AND author = :author"
            params["author"] = user_id
        if limit:
            sql += " LIMIT :limit"
            params["limit"] = limit
        self.cur.execute(sql)
        return self.cur.fetchall()
    
    def insert_submission(self, keyword, url, author, desc = None, meta_title = None, meta_desc = None):
        self.cur.execute("""INSERT INTO submissions (keyword, url, author, desc, meta_title, meta_description) 
                            VALUES (?, ?, ?, ?, ?, ?)""",
                            (keyword, url, author, desc, meta_title, meta_desc))
        self.conn.commit()

