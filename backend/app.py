from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import os
import json

app = Flask(__name__)
CORS(app)

DB_NAME = 'omni_db'
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'
DB_HOST = 'localhost'
DB_PORT = '5432'

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
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 