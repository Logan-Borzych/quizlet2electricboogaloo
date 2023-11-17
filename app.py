from flask import Flask, render_template, request, redirect, url_for, logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from datetime import datetime
import logging
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
    set_id = db.Column(db.Integer, db.ForeignKey('set.id'), nullable=False)


class Set(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    terms = db.relationship('Term', backref='set', lazy=True)



#ROUTES TO RENDER WEBPAGE AND DETERMINE ROUTES FOR WEBPAGES

#homepage
@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')

#features page (tbh i dont know what this is for)
@app.route('/features', methods=['GET','POST'])
def features():
    return render_template('featureselect.html')

#routes to home for now, i dont know what this page is for
#create page (functionality is questionable)
@app.route('/home', methods=['get','post'])
def createPage():
    return render_template('create.html')

@app.route('/create')
def create():
    return render_template('create.html')

# create_set route
@app.route('/create_set', methods=['GET', 'POST'])
def create_set():
    if request.method == "POST":
        set_name = request.form['name']

        new_set = Set(name=set_name)

        try:
            db.session.add(new_set)
            db.session.commit()

            app.logger.debug(f"Redirecting to: {url_for('specific_sets', set_id=new_set.id)}")
            
            # Use url_for to generate the URL for  specific_sets
            return redirect(url_for('specific_sets', set_id=new_set.id))
        except Exception as e:
            app.logger.error(f"Error: {e}")
            return "check console"
    else:
        return render_template('create_set.html')




#currently goes to flashcard page ----------- in future i think we should split
#                                             this into term creation and flashcards
@app.route('/sets/<int:set_id>', methods=['GET', 'POST'])
def specific_sets(set_id):
    if request.method == "POST":
        termForm = request.form['term']
        definitionForm = request.form['definition']
        
        # Query the set based on its ID
        set_data = Set.query.get_or_404(set_id)
        
        # Create a new Term object and add it to the database
        pair = Term(term=termForm, definition=definitionForm, set_id=set_id)
        
        try:
            db.session.add(pair)
            db.session.commit()
            return redirect(url_for('specific_sets', set_id=set_id))
        except Exception as e:
            print(f"Error: {e}")
            return "Oops! Something went wrong."

    else:
        # Load database terms based on the set ID
        set_data = Set.query.get_or_404(set_id)
        terms = Term.query.filter_by(set_id=set_id).all()
        return render_template('sets.html', set_data=set_data, terms=terms, set_id=set_id)



#allows the user to update their database entry
@app.route('/sets/<string:set_id>/edit/<int:term_id>', methods=['GET', 'POST'])
def edit_pair(set_id, term_id):
    # Requests the database entry for the pair that the user wants to update
    pair_to_update = Term.query.get_or_404(term_id)

    if request.method == "POST":
        # Update the pair with the form data
        pair_to_update.term = request.form['term']
        pair_to_update.definition = request.form['definition']

        try:
            # Commit changes to the database
            db.session.commit()
            # Redirect to the specific_sets route
            return redirect(url_for('specific_sets', set_id=set_id))
        except Exception as e:
            print(f"Error: {e}")
            return "Oops"
    else:
        # Render the edit form when it's a GET request
        return render_template('editPair.html', term=pair_to_update, set_id=set_id)

#deletes a pair
@app.route('/sets/<int:set_id>/delete/<int:term_id>')
def delete_pair(term_id, set_id):
    delete_pair = Term.query.get_or_404(term_id)
    try:
        db.session.delete(delete_pair)
        db.session.commit()
        return redirect(url_for('specific_sets', set_id=set_id))
    except Exception as e:
        print(f"Error: {e}")
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

@app.route('/explore', methods=['GET'])
def explore():
    results = []
    return render_template('explore.html', results=results)


@app.route('/explore/search', methods=['POST'])
def search_explore():
    query = request.form.get('query')
    results = Set.query.filter(or_(
        Set.name.ilike(f"%{query}%")
    )).all()
    return render_template('explore.html', results=results)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    app.run()