#import all libs
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

#init tree
app = Flask(__name__)

#define the SQLite database file
db_path = "../databases/flashcards.db"

def connect_db():
    return sqlite3.connect(db_path)

@app.route('/')
def index():
    return render_template('../templates/flashcards.html')

@app.route('/submit', methods=['POST'])
def submit():
    card_name = request.form['card_name']
    card_def = request.form['card_def']

    # Insert the form data into the database
    with connect_db() as db:
        cursor = db.cursor()
        cursor.execute("INSERT INTO carddata (setID, cardName, cardDef) VALUES (?, ?, ?)",
                       (set_number, card_name, card_def))
        db.commit()

    return redirect(url_for('index'))



