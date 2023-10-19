from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

app.config['DATABASE'] = 'flashcards.db'

def get_db():
    db = getattr(app, '_database', None)
    if db is None:
        db = app._database = sqlite3.connect(app.config['DATABASE'])
    return db

@app.teardown_appcontext
def close_db(error):
    db = getattr(app, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.route('/')
def index():
    # Fetch flashcard entries from the database
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM flashcards")
    flashcards = cursor.fetchall()
    return render_template('index.html', flashcards=flashcards)

@app.route('/add_flashcard', methods=['POST'])
def add_flashcard():
    question = request.form['question']
    answer = request.form['answer']

    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO flashcards (question, answer) VALUES (?, ?)", (question, answer))
    db.commit()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)