from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flashcards.db'

db = SQLAlchemy(app)

class Term(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    setID = db.Column(db.Integer)
    term = db.Column(db.String(255), nullable=False)
    definiition = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return '<name %r>' % self.id

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')

@app.route('/features', methods=['GET','POST'])
def features():
    return render_template('featureselect.html')

@app.route('/sets', methods=['GET','POST'])
def sets():
    if request.method == "POST"
        term = request.form["question"]
        definitionA = request.form["answer"]
    return render_template('flashcards.html')


if __name__ == '__main__':
    app.run()
