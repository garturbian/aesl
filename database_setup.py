
import sqlite3

def setup_database():
    conn = sqlite3.connect('aesl.db')
    c = conn.cursor()

    # Create words table
    c.execute('''
        CREATE TABLE IF NOT EXISTS words (
            word_id INTEGER PRIMARY KEY,
            lemma TEXT NOT NULL,
            pos TEXT,
            frequency_rank INTEGER,
            definition TEXT,
            translation TEXT,
            morphology TEXT
        )
    ''')

    # Create reviews table
    c.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            review_id INTEGER PRIMARY KEY,
            word_id INTEGER,
            interval_days INTEGER,
            last_review_date TEXT,
            next_review_date TEXT,
            easiness_score REAL,
            correct_count INTEGER,
            wrong_count INTEGER,
            FOREIGN KEY (word_id) REFERENCES words (word_id)
        )
    ''')

    # Create examples table
    c.execute('''
        CREATE TABLE IF NOT EXISTS examples (
            example_id INTEGER PRIMARY KEY,
            word_id INTEGER,
            sentence TEXT NOT NULL,
            source TEXT,
            date_created TEXT,
            FOREIGN KEY (word_id) REFERENCES words (word_id)
        )
    ''')

    # Create user_settings table
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            id INTEGER PRIMARY KEY,
            preferred_language TEXT,
            review_mode TEXT,
            last_sync TEXT
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    setup_database()
    print("Database setup complete.")
