from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flashcards.db'

db = SQLAlchemy(app)

class Term(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(255), nullable=False)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/features')
def features():
    return render_template('featureselect.html')

@app.route('/sets')
def sets():
    return render_template('flashcards.html')

if __name__ == '__main__':
    app.run()
