import sqlite3

class Vocabulary():
    def __init__(self, path):
	    self.db_file = path

    def read(self):
	    """
	    	Fetching
	    """
	    conn = sqlite3.connect(self.db_file)
	    c = conn.cursor()
	    return c.execute("SELECT LOWER(w.word), l.usage FROM LOOKUPS as l INNER JOIN WORDS as w ON l.word_key = w.id")

