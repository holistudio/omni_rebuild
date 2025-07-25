from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2

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

if __name__ == '__main__':
    app.run(debug=True) 