from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import os
import json
from dotenv import load_dotenv
import requests

app = Flask(__name__)
CORS(app)

DB_NAME = 'omni_db'
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'
DB_HOST = 'localhost'
DB_PORT = '5432'

load_dotenv()
GOOGLE_BOOKS_API_KEY = os.getenv('GOOGLE_BOOKS_API_KEY')

@app.route('/')
def index():
    return jsonify({"message": "Welcome to the OmniRebuild backend!"})

@app.route('/questions')
def get_questions():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cur = conn.cursor()
    cur.execute('SELECT question FROM questions ORDER BY id ASC;')
    questions = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify({"questions": questions})

@app.route('/save_conversation', methods=['POST'])
def save_conversation():
    data = request.get_json()
    if not data or 'conversation' not in data:
        return jsonify({'error': 'No conversation data provided'}), 400
    conversation = data['conversation']
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(backend_dir, 'conversation.json')
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(conversation, f, ensure_ascii=False, indent=2)
        # Concatenate all user responses and write to search_prompt.txt
        responses = [str(entry.get('response', '')) for entry in conversation]
        prompt = ' '.join(responses)
        # Remove articles, personal pronouns, and prepositions
        articles_pronouns_preps = set([
            'a', 'an', 'the',
            'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'me', 'him', 'her', 'us', 'them',
            'my', 'your', 'his', 'its', 'our', 'their',
            # Common prepositions
            'about', 'above', 'across', 'after', 'against', 'along', 'among', 'around', 'at',
            'before', 'behind', 'below', 'beneath', 'beside', 'between', 'beyond', 'but', 'by',
            'concerning', 'despite', 'down', 'during', 'except', 'for', 'from', 'in', 'inside',
            'into', 'like', 'near', 'of', 'off', 'on', 'onto', 'out', 'outside', 'over', 'past',
            'regarding', 'since', 'through', 'throughout', 'to', 'toward', 'under', 'underneath',
            'until', 'up', 'upon', 'with', 'within', 'without'
        ])
        filtered_words = [w for w in prompt.split() if w.lower() not in articles_pronouns_preps]
        filtered_prompt = ' '.join(filtered_words)
        prompt_path = os.path.join(backend_dir, 'search_prompt.txt')
        with open(prompt_path, 'w', encoding='utf-8') as pf:
            pf.write(filtered_prompt)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search_books', methods=['GET'])
def search_books():
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(backend_dir, 'search_prompt.txt')
    if not os.path.exists(prompt_path):
        return jsonify({'error': 'search_prompt.txt not found'}), 404
    with open(prompt_path, 'r', encoding='utf-8') as f:
        query = f.read().strip()
    if not query:
        return jsonify({'error': 'Empty search prompt'}), 400
    if not GOOGLE_BOOKS_API_KEY:
        return jsonify({'error': 'Google Books API key not set'}), 500
    url = 'https://www.googleapis.com/books/v1/volumes'
    params = {
        'q': query,
        'key': GOOGLE_BOOKS_API_KEY,
        'maxResults': 10
    }
    try:
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        books = []
        for item in data.get('items', []):
            volume = item.get('volumeInfo', {})
            books.append({
                'title': volume.get('title'),
                'authors': volume.get('authors'),
                'description': volume.get('description'),
                'thumbnail': volume.get('imageLinks', {}).get('thumbnail'),
                'infoLink': volume.get('infoLink')
            })
        # Write results to search_results.json
        results_path = os.path.join(backend_dir, 'search_results.json')
        with open(results_path, 'w', encoding='utf-8') as rf:
            json.dump(books, rf, ensure_ascii=False, indent=2)
        return jsonify({'books': books})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 