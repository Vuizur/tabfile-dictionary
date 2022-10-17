
from dataclasses import dataclass
import sqlite3

@dataclass
class Entry:
    word: str
    definition: str

class TabfileDictionary:
    def __init__(self, filename: str, in_memory = True, temp_sqlite_path = None):
        self.filename = filename
        self.in_memory = in_memory
        self.temp_sqlite_path = temp_sqlite_path
        self._load()

    def _load(self):
        """Loads the dictionary from the file into an SQLite database"""
        if self.in_memory:
            self.db = sqlite3.connect(":memory:")
        else:
            # Make sure the temp_sqlite_path is set
            if self.temp_sqlite_path is None:
                raise ValueError("temp_sqlite_path must be set if in_memory is False")
            self.db = sqlite3.connect(self.temp_sqlite_path)
        
        self.cursor = self.db.cursor()

        # Create a table with headword and definition
        self.db.execute("""CREATE TABLE dictionary (
            headword_id INTEGER NOT NULL PRIMARY KEY, 
            headword TEXT,
            definition TEXT, 
            headword_lower TEXT)""")
        # Create a table with inflected forms and their headword
        self.db.execute("""CREATE TABLE inflections (
            inflection_id INTEGER NOT NULL PRIMARY KEY,
            inflection_lower TEXT,
            headword_id INTEGER,
            FOREIGN KEY (headword_id) REFERENCES dictionary (headword_id))""")

        with open(self.filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if "\t" in line:
                    line = line.split('\t')
                    definition = line[1]
                    headword_and_inflections = line[0].split('|')
                    headword = headword_and_inflections[0]
                    inflections = headword_and_inflections[1:]
                    # Insert the headword and definition into the dictionary table
                    self.db.execute("INSERT INTO dictionary (headword, definition, headword_lower) VALUES (?, ?, ?)", (headword, definition, headword.lower()))
                    # Get the last inserted row id
                    headword_id = self.db.execute("SELECT last_insert_rowid()").fetchone()[0]
                    # Insert the inflections into the inflections table
                    for inflection in inflections:
                        self.db.execute("INSERT INTO inflections (inflection_lower, headword_id) VALUES (?, ?)", (inflection.lower(), headword_id))


        # Add indices
        self.db.execute("CREATE INDEX headword_lower_index ON dictionary (headword_lower)")
        self.db.execute("CREATE INDEX inflection_lower_index ON inflections (inflection_lower)")
        # Index foreign key
        self.db.execute("CREATE INDEX headword_id_index ON inflections (headword_id)")
        
        self.db.commit()


    def lookup(self, word: str) -> list[Entry]:
        """Looks up a word in the dictionary and returns a list of entries"""
        # Look up the word in the dictionary table
        self.cursor.execute("SELECT headword, definition FROM dictionary WHERE headword_lower = ?", (word.lower(),))
        entries = self.cursor.fetchall()
        all_entries: list[Entry] = []
        if len(entries) > 0:
            for entry in entries:
                all_entries.append(Entry(entry[0], entry[1]))
        # Look up the word in the inflections table
        self.cursor.execute("SELECT headword, definition FROM dictionary INNER JOIN inflections ON dictionary.headword_id = inflections.headword_id WHERE inflection_lower = ?", (word.lower(),))
        entries = self.cursor.fetchall()
        if len(entries) > 0:
            for entry in entries:
                all_entries.append(Entry(entry[0], entry[1]))
        return all_entries
        

def usage_example():
    import time
    start = time.time()
    dictionary = TabfileDictionary("spa_eng.txt")
    end = time.time()
    print(f"Loading the dictionary took {end - start} seconds")
    # Benchmarking
    start = time.time()
    entries = dictionary.lookup("oso")
    for entry in entries:
        print(entry.word, entry.definition)
    end = time.time()

    # Time taken in milliseconds
    print(f"Time taken: {(end - start) }s")


if __name__ == "__main__":
    usage_example()