from flask import Flask, jsonify, request, send_from_directory
import sqlite3
from scheduler import update_review_status
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def send_static(path):
    return send_from_directory('.', path)

@app.route('/api/next-word')
def get_next_word():
    conn = sqlite3.connect('aesl.db')
    c = conn.cursor()
    # Get the word with the nearest next_review_date
    c.execute("SELECT w.word_id, w.lemma, w.definition FROM words w JOIN reviews r ON w.word_id = r.word_id ORDER BY r.next_review_date ASC LIMIT 1")
    word_data = c.fetchone()
    conn.close()

    if word_data:
        word = {
            'word_id': word_data[0],
            'lemma': word_data[1],
            'definition': word_data[2]
        }
    else:
        word = {
            'word_id': 0,
            'lemma': 'No words to review',
            'definition': 'Add some words to get started!'
        }
    return jsonify(word)

@app.route('/api/update-status', methods=['POST'])
def update_status():
    data = request.get_json()
    word_id = data.get('word_id')
    correct = data.get('correct')

    update_review_status(word_id, correct)

    print(f"Received update for word_id: {word_id}, correct: {correct}")

    return jsonify({'status': 'success'})

@app.route('/api/examples/<int:word_id>')
def get_examples(word_id):
    conn = sqlite3.connect('aesl.db')
    c = conn.cursor()
    c.execute("SELECT lemma FROM words WHERE word_id = ?", (word_id,))
    lemma_data = c.fetchone()
    conn.close()

    if lemma_data:
        lemma = lemma_data[0]
        prompt = f"Provide 3 simple and clear example sentences for the word '{lemma}', suitable for an A2-B1 level ESL learner."
        
        try:
            # It's better to use the Ollama Python library if available, 
            # but for simplicity, we'll use subprocess for now.
            result = subprocess.run(
                ['ollama', 'run', 'gemma3:4b', prompt],
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8'
            )
            examples = result.stdout.strip().split('\n')
            return jsonify(examples)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Error calling Ollama: {e}")
            return jsonify({'error': 'Failed to generate examples.'}), 500
    else:
        return jsonify({'error': 'Word not found.'}), 404

if __name__ == '__main__':
    app.run(debug=True)
