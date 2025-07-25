import psycopg2

# Update these values as needed for your local setup
DB_NAME = 'omni_db'
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'
DB_HOST = 'localhost'
DB_PORT = '5432'

QUESTIONS = [
    "What types of stories (books, movies, TV shows, podcasts) do you find yourself drawn to most often?",
    "Is there a particular genre or theme you never get tired of exploring?",
    "Can you share a book or story that had a big impact on you in the past? What made it memorable?",
    "Are there any authors whose writing style you especially enjoy or dislike?",
    "Do you prefer stories with fast-paced plots, deep character development, or rich world-building?",
    "What’s a book, film, or show you recently enjoyed, and what did you like about it?",
    "Are there any topics or genres you’re not interested in or actively avoid?",
    "Do you enjoy stories that challenge your perspective, or do you prefer comfort reads?",
    "How do you usually discover new books or stories to enjoy?",
    "Is there a story you wish existed, or a topic you’d love to read more about?"
]

def create_table_and_insert_questions():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id SERIAL PRIMARY KEY,
            question TEXT NOT NULL
        );
    ''')
    cur.execute('DELETE FROM questions;')  # Clear existing for idempotency
    for q in QUESTIONS:
        cur.execute('INSERT INTO questions (question) VALUES (%s);', (q,))
    conn.commit()
    cur.close()
    conn.close()
    print('Questions table created and populated.')

if __name__ == '__main__':
    create_table_and_insert_questions() 