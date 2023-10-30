from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///terms.db'

db = SQLAlchemy(app)


#to start app use "python app.py" in the command line
#to stop, use ctrl+C in terminal
#class definition for database entries
class Term(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(255), nullable=False)
    definition = db.Column(db.String(255), nullable=False)

    #i still dont know what this means
    def __repr__(self):
        return '<name %r>' % self.id

#ROUTES TO RENDER WEBPAGE AND DETERMINE ROUTES FOR WEBPAGES

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
def specificSets():

    if request.method == "POST":

        #grabs term and definition
        termForm = request.form['term']
        definitionForm = request.form['definition']

        #creates new Term objects and adds to database
        pair = Term(term=termForm, definition=definitionForm)

        #pushes Term object to the database
        try:
            db.session.add(pair)
            db.session.commit()
            return redirect(url_for('specificSets'))
        except Exception as e:
            print(f"Error: {e}")
            return "so like, we messed up big time"

    else:
        #loads database terms
        pairs = Term.query.order_by(Term.id)
        return render_template('sets.html', pairs=pairs)

#allows the user to update their database entry
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def editPair(id):
    # Requests the database entry for the pair that the user wants to update
    pairToUpdate = Term.query.get_or_404(id)

    # When the user edits the pair, commit to the database
    if request.method == "POST":
        pairToUpdate.term = request.form['term']
        pairToUpdate.definition = request.form['definition']
        try:
            db.session.commit()
            return redirect('/sets')
        except:
            return "Oops"
    else:
        # Activates upon arrival to the page
        return render_template('editPair.html', Term=pairToUpdate)

#deletes a pair
@app.route('/delete/<int:id>')
def deletePari(id):
    deletePair = Term.query.get_or_404(id)
    try:
        db.session.delete(deletePair)
        db.session.commit()
        return redirect('/sets')
    except:
        return "Oops"
    

#matching game page
@app.route('/match', methods=['GET', 'POST'])
def match():
    return render_template('matching.html')

#login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

#sign up page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template('signup.html')

if __name__ == '__main__':
    app.run()
