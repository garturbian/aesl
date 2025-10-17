import sqlite3
from datetime import datetime, timedelta
import requests
import json

def seed_database():
    conn = sqlite3.connect('aesl.db')
    c = conn.cursor()

    # Words to remove (old words)
    words_to_remove = [2, 3, 4]
    for word_id in words_to_remove:
        c.execute("DELETE FROM reviews WHERE word_id = ?", (word_id,))
        c.execute("DELETE FROM words WHERE word_id = ?", (word_id,))

    words_to_add = [
        (2, 'journey', 'An act of traveling from one place to another.'),
        (3, 'delicious', 'Highly pleasant to the taste.'),
        (4, 'curious', 'Eager to know or learn something.')
    ]

    for word in words_to_add:
        c.execute("INSERT OR IGNORE INTO words (word_id, lemma, definition) VALUES (?, ?, ?)", word)
        word_id = word[0]
        
        # Fetch morphology from the API
        try:
            response = requests.get(f"http://127.0.0.1:5000/api/morphology/{word_id}")
            if response.status_code == 200:
                morphology_json = response.json()
                c.execute("UPDATE words SET morphology = ? WHERE word_id = ?", (json.dumps(morphology_json), word_id))
        except requests.exceptions.ConnectionError:
            print(f"Could not connect to the server at http://127.0.0.1:5000. Please ensure the Flask server is running and accessible.")
            break  # Exit the loop if the server is not available
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching morphology for word_id {word_id}: {e}")

        # Initialize review for the word
        c.execute("""
            INSERT OR IGNORE INTO reviews (word_id, interval_days, last_review_date, next_review_date, easiness_score, correct_count, wrong_count)
            VALUES (?, 1, ?, ?, 2.5, 0, 0)
        """, (word_id, datetime.now().strftime("%Y-%m-%d"), (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")))

    conn.commit()
    conn.close()
    print("Database seeded with sample words and morphology.")

if __name__ == '__main__':
    seed_database()