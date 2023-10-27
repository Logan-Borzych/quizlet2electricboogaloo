from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flashcards.db'

db = SQLAlchemy(app)

#class definition for database entries
class Term(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    setID = db.Column(db.Integer)
    term = db.Column(db.String(255), nullable=False)
    definiition = db.Column(db.String(255), nullable=False)

    #i still dont know what this means
    def __repr__(self):
        return '<name %r>' % self.id


#ROUTES TO RENDER WEBPAGE AND DETERMINE ROUTES FOR WEBPAGES
#NEED TO ADD: login/signup

#homepage
@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')

#features page (tbh i dont know what this is for)
@app.route('/features', methods=['GET','POST'])
def features():
    return render_template('featureselect.html')

#create page (functionality is questionable)
@app.route('/create', methods=['get','post'])
def createPage():
    return render_template('create.html')

#currently goes to flashcard page ----------- in future i think we should split
#                                             this into term creation and flashcards
@app.route('/sets', methods=['GET','POST'])
def sets():
    if request.method == "POST"
        term = request.form["question"]
        definitionA = request.form["answer"]
    return render_template('flashcards.html')

#matching game page
@app.route('/match', methods=['GET', 'POST'])
def match():
    return render_template('matching.html')

if __name__ == '__main__':
    app.run()
