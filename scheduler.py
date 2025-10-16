
import sqlite3
from datetime import datetime, timedelta

def update_review_status(word_id: int, correct: bool):
    conn = sqlite3.connect('aesl.db')
    c = conn.cursor()

    c.execute("SELECT interval_days, easiness_score FROM reviews WHERE word_id = ?", (word_id,))
    result = c.fetchone()

    if result:
        current_interval, easiness_score = result
    else:
        # If it's a new word, initialize with default values
        current_interval, easiness_score = 1, 2.5
        c.execute("INSERT INTO reviews (word_id, interval_days, last_review_date, next_review_date, easiness_score, correct_count, wrong_count) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (word_id, current_interval, datetime.now().strftime("%Y-%m-%d"), (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"), easiness_score, 0, 0))


    if correct:
        new_interval = current_interval * easiness_score
        c.execute("UPDATE reviews SET correct_count = correct_count + 1 WHERE word_id = ?", (word_id,))
    else:
        new_interval = 1  # Reset to 1 day if incorrect
        c.execute("UPDATE reviews SET wrong_count = wrong_count + 1 WHERE word_id = ?", (word_id,))

    last_review_date = datetime.now()
    next_review_date = last_review_date + timedelta(days=int(new_interval))

    c.execute("""
        UPDATE reviews
        SET
            interval_days = ?,
            last_review_date = ?,
            next_review_date = ?
        WHERE word_id = ?
    """, (new_interval, last_review_date.strftime("%Y-%m-%d"), next_review_date.strftime("%Y-%m-%d"), word_id))

    conn.commit()
    conn.close()


