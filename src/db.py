import sqlite3
import os
from collections import namedtuple

def namedtuple_factory(cursor, row):
    """Returns sqlite rows as named tuples."""
    fields = [col[0] for col in cursor.description]
    Row = namedtuple("Row", fields)
    return Row(*row)

class Database:
    def __init__(self, path):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = namedtuple_factory
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
            )'''
        )

        self.cur.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS search_sub USING fts5 (
                keywords, description, meta_title, meta_description, url, author, created_on
            )
        ''')

        # for now keep it as a duplicate
        self.cur.execute('''
            CREATE TRIGGER IF NOT EXISTS insert_submission_trigger 
            AFTER INSERT ON submissions 
            BEGIN 
            INSERT OR IGNORE INTO search_sub
            VALUES (NEW.keywords, NEW.description, NEW.meta_title, NEW.meta_description, NEW.url, NEW.author, NEW.created_on);
            END;
        ''')

    def get_submissions(self):
        self.cur.execute("SELECT * FROM submissions")
        return self.cur.fetchall()

    def get_submission_by_id(self, id):
        self.cur.execute("SELECT * FROM submissions WHERE id = ?", (id,))
        return self.cur.fetchone()

    def get_submissions_by_query(self, query, user_id, limit):
        query = query.replace("'\\\"", "\"").replace("\\\"'", "\"").replace("\\\"", "\"").replace("\\\"", "\"")
        print(query)
        sql = """SELECT * FROM search_sub WHERE 1"""
        params = {}
        if query:
            sql += " AND search_sub MATCH :query"
            params["query"] = query
        if user_id:
            sql += " AND author = :author"
            params["author"] = user_id
        if limit:
            sql += " LIMIT :limit"
            params["limit"] = limit
        sql += " ORDER BY bm25(search_sub)"
        self.cur.execute(sql, params)
        return self.cur.fetchall()
    
    def insert_submission(self, keyword, url, author, desc = None, meta_title = None, meta_desc = None):
        self.cur.execute("""INSERT INTO submissions (keywords, url, author, description, meta_title, meta_description) 
                            VALUES (?, ?, ?, ?, ?, ?)""",
                            (keyword, url, author, desc, meta_title, meta_desc))
        self.conn.commit()
        return self.cur.lastrowid
