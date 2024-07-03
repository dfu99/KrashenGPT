import sqlite3
import numpy as np
from app import gpt
import os

def db_is_empty(language):
    """
    Check if the database is empty
    """
    database_name = os.path.join("instance",language+".db")
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    content = cursor.execute("SELECT name FROM sqlite_master")
    if not content.fetchall():
        return True
    return False


class language_database:
    """
    Accessor object
    Handles accesse and calls to the SQLite database
    Helps define our to_sql and from_sql wrappers
    """
    def __init__(self, language):
        self.language=language
        self.database_name = os.path.join("instance",language+".db")
        self.conn = None
        self.cursor = None
    
    def to_sql(self, func):
        try:
            # Connect to the database
            self.conn = sqlite3.connect(self.database_name)
            self.cursor = self.conn.cursor()
            # Execute the SQLite query
            func()
            last_id = self.cursor.lastrowid
            return last_id
        
        except sqlite3.Error as e:
            # Pass through errors
            print(f"An error occurred in {func.__name__}: {e}")
            return None
        
        finally:
            # Commit the changes
            self.conn.commit()
            # Close the connection
            if self.conn:
                self.conn.close()

    def from_sql(self, func):
        try:
            # Connect to the database
            self.conn = sqlite3.connect(self.database_name)
            self.cursor = self.conn.cursor()
            # Execute the SQLite query
            return func()
        
        except sqlite3.Error as e:
            # Pass through errors
            print(f"An error occurred in {func.__name__}: {e}")
            return None
        
        finally:
            # Close the connection
            if self.conn:
                self.conn.close()

    def make_sql_table(self, table_name):
        """
        Add a new database for a language
        Databases are named per language and contain tables per part of speech

        :param database_name: Name of the SQLite database file
        :param table_name: Name of the table to make
        """
        def action(table_name):
            self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (word TEXT PRIMARY KEY NOT NULL UNIQUE, score INTEGER DEFAULT 0)")
        
        # Formatting
        table_name = table_name.replace(" ", "")
        self.to_sql(lambda: action(table_name))

    def add_vocab_to_sql(self, table_name, text_value):
        """
        Add a row with text and integer values to a SQLite3 database table.

        :param database_name: Name of the SQLite database file
        :param table_name: Name of the table to insert into
        :param text_value: The text value to insert
        :return: ID of the inserted row
        """
        def action(table_name, text_value):
            # Insert the row
            self.cursor.execute(f"INSERT INTO {table_name}(word, score) VALUES('{text_value}', 0) ON CONFLICT(word) DO NOTHING")
        # Formatting
        table_name = table_name.replace(" ", "")
        self.to_sql(lambda: action(table_name, text_value))

    def inc_vocab_score(self, table_name, text_value, score_delta=1):
        """
        Find the text_value in the database and table, then add score_delta to the existing score
        """
        table_name = table_name.replace(" ", "")
        def action(table_name, text_value, score_delta):
            # Insert the row
            self.cursor.execute(f"UPDATE {table_name} SET score=score+{score_delta} WHERE word = '{text_value}'")
        self.to_sql(lambda: action(table_name, text_value, score_delta))
    
    def get_rows(self, table_name, numrows):
        """
        Get the top numrows of the table, sorted by score
        """
        table_name = table_name.replace(" ", "")
        def action(table_name):
            # Retrieve the data
            rows = self.cursor.execute(f"SELECT word, score FROM {table_name} ORDER BY score ASC").fetchall()
            return rows[:numrows]
        return self.from_sql(lambda: action(table_name))
    
    def mean_score(self):
        """
        Gets the average score of all entries in the merged tables
        """
        def action():
            output = self.cursor.execute("SELECT avg(score) FROM merged").fetchall()
            return float(output[0][0])
        return self.from_sql(lambda: action())

    def get_batch(self, batch_size, parts=None):
        """
        Makes a batch from database of size (batch_size)
        :return: dicts of the batches and scores with corresponding indices
        """
        batch = {}
        scores = {}
        # If organized by parts
        if parts:
            for p in parts:
                batch[p] = []
                scores[p] = {}
                data = self.get_rows(p, batch_size)                
                for line in data:
                    batch[p].append(line[0])
                    scores[p][line[0]] = 0
        # Otherwise pull from the merged table and put everything in the same dict
        else:
            batch['words'] = []
            scores['words'] = {}
            data = self.get_rows('merged', batch_size)
            for line in data:
                batch['words'].append(line[0])
                scores['words'][line[0]] = 0
        return batch, scores
    
    def grow_batch(self, parts_of_speech, contexts, new_batch_size):
        """
        Add more words into the database
        """
        for p, c in zip(parts_of_speech, contexts):
            self.make_sql_table(p)
            new_batch = gpt.generate_batch(p, self.language, c, size=new_batch_size)
            for word in new_batch:
                # Add to the parts of speech table
                self.add_vocab_to_sql(p, word)
                # Add everything into merged table
                self.add_vocab_to_sql('merged', word)