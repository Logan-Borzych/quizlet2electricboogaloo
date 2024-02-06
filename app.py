from flask import Flask, render_template, request, redirect, url_for, logging
from flask_sqlalchemy import SQLAlchemy
from fuzzywuzzy import process
from flask_migrate import Migrate
from functions import *
import logging
import random

#fart

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///terms.db'

db = SQLAlchemy(app)
migrate = Migrate(app, db)


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
    terms = db.relationship('Term', backref='set', cascade='all, delete-orphan', lazy=True)



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


#i have no idea what this does dont touch it
@app.route('/sets', methods=['GET', 'POST'])
def sets_main():
    if request.method == 'POST':
        query = request.form.get('query', '')
        all_sets = Set.query.all()
        # Use fuzzy matching to find sets with names similar to the query
        sets_with_scores = [(set_obj, process.extractOne(query, [set_obj.name])) for set_obj in all_sets]
        # Filter out sets with a score below a certain threshold (e.g., 70)
        threshold = 0
        sets = [set_obj for set_obj, score in sets_with_scores if score[1] >= threshold]
        # Perform an exact match check
        exact_matches = Set.query.filter_by(name=query).all()
        sets_with_scores += [(set_obj, (100, 0)) for set_obj in exact_matches]

        # Sort the results by similarity score
        sets_with_scores = sorted(sets_with_scores, key=lambda x: x[1][1], reverse=True)
        sets = [set_obj for set_obj, score in sets_with_scores if score[1] >= threshold]

        return render_template('sets_main.html', sets=sets, query=query)
    
    else:
        # Render the initial sets_main page
        return render_template('sets_main.html', sets=None, query=None)
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

@app.route('/')
def index():
    # Fetch sets from the database
    sets = get_sets_from_database()
    return render_template('index.html', sets=sets)

@app.route('/delete_set/<int:set_id>', methods=['POST'])
def delete_set(set_id):
    # Delete set from the database
    delete_set_from_database(set_id)
    return redirect('/')

def get_sets_from_database():
    # Fetch sets from the database
    with sqlite.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM sets')
        sets = cursor.fetchall()
    return sets

def delete_set_from_database(set_id):
    # Delete set from the database
        delete_set = Set.query.get_or_404(set_id)
        db.session.delete(delete_set)
        db.session.commit()
        return redirect(url_for('index'))
    
def delete_all_entries_for_set_id(set_id):
    # Deletes flashcards for a set from the database
        db.session.query(term).filter_by(set_id).delete()
        db.session.commit()
    
#Quiz feature page
@app.route('/quizSetUp/<int:set_id>', methods=['GET', 'POST'])
def quizSetUp(set_id):
    print("Inside quizSetUp route")
    raw_set_data = Set.query.get_or_404(set_id)
    app.logger.info(raw_set_data)
    num_terms = Term.query.filter_by(set_id=set_id).count()

    return render_template('quiz_SetUp.html', set_id=set_id, set_data=raw_set_data, num_terms=num_terms)

@app.route('/quiz/<int:set_id>/<int:amount_of_questions>', methods=['GET', 'POST'])
def quiz(set_id, amount_of_questions):
    print("Inside quiz route")
    raw_set_data = Set.query.get_or_404(set_id)
    app.logger.info(raw_set_data)
    #Creates the list of flashcard ids that will be used for the quiz
    max_number = Term.query.filter_by(set_id=set_id).count()
    question_ids = random.sample(range(1, max_number + 1), amount_of_questions)
    random.shuffle(question_ids)
    questions = [{"id": question_id, "data": questionCreate(set_id, question_id)} for question_id in question_ids]
    terms_data = Term.query.filter_by(set_id=set_id).all()
    term_names = [term.term for term in terms_data]
    definitions = [term.definition for term in terms_data]
    app.logger.info("Term Names: %s", term_names)
    app.logger.info("Definitions: %s", definitions)
    return render_template('quiz.html', set_id=set_id, set_data=raw_set_data, questions=questions, term_names=term_names, definitions=definitions)

@app.route('/quiz/<int:set_id>/', methods=['GET', 'POST'])
def quizCustomRoute(set_id):
    print("Inside quiz route")
    raw_set_data = Set.query.get_or_404(set_id)
    app.logger.info(raw_set_data)
    #Creates the list of flashcard ids that will be used for the quiz
    max_number = Term.query.filter_by(set_id=set_id).count()
    #Pulls answer given for amount of questions
    amount_of_questions = int(request.form.get('question_slide'))
    question_ids = random.sample(range(1, max_number + 1), amount_of_questions)
    random.shuffle(question_ids)
    questions = [{"id": question_id, "data": questionCreate(set_id, question_id)} for question_id in question_ids]
    terms_data = Term.query.filter_by(set_id=set_id).all()
    term_names = [term.term for term in terms_data]
    definitions = [term.definition for term in terms_data]
    app.logger.info("Term Names: %s", term_names)
    app.logger.info("Definitions: %s", definitions)
    return render_template('quiz.html', set_id=set_id, set_data=raw_set_data, questions=questions, term_names=term_names, definitions=definitions)

def questionCreate(set_id, flashcard_id):
    #Creates the list of flaschard ids that wil be used in a question
    right_answer_id = flashcard_id - 1
    max_number = Term.query.filter_by(set_id=set_id).count()
    wrong_answers = random.sample([number for number in range(1, max_number + 1) if number != right_answer_id + 1], 3)
    wrong_answers.append(right_answer_id + 1)
    random.shuffle(wrong_answers)

    return wrong_answers, right_answer_id

@app.route('/quizResults/<int:set_id>', methods=['POST'])
def quizResults(set_id):
    raw_set_data = Set.query.get_or_404(set_id)
    terms_data = Term.query.filter_by(set_id=set_id).all()
    definitions = [term.definition for term in terms_data]
    user_answers = {key.split('_')[1]: int(value) for key, value in request.form.items() if key.startswith('answers')}
    results = []
    for question_id, user_answer in user_answers.items():
        right_answer_id = int(question_id)
        correct_answer = definitions[right_answer_id]
        if user_answer == right_answer_id + 1:
           results.append({"question_id": int(question_id), "correct": True, "user_answer": correct_answer, "correct_answer": correct_answer})
        else:
           results.append({"question_id": int(question_id), "correct": False, "user_answer": definitions[user_answer - 1], "correct_answer": correct_answer})
    app.logger.info("Form Data: %s", request.form)
    app.logger.info("User Answers: %s", user_answers)
    app.logger.info("Results: %s", results)
    return render_template('quizResults.html', set_id=set_id, results=results, set_data=raw_set_data, definitions=definitions)

#matching game page
@app.route('/match/<int:set_id>', methods=['GET', 'POST'])
def match(set_id):
    print("Inside match route")
    raw_set_data = Set.query.get_or_404(set_id)
    app.logger.info(raw_set_data)

    return render_template('match_main.html')

@app.route('/match_old', methods=['GET', 'POST'])
def match_old():
    return render_template('matching.html')

#login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

#sign up page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template('signup.html')

@app.route('/flashcards', methods=['GET'])
def flashcards():
    return render_template('flashcards.html')

@app.route('/explore', methods=['GET', 'POST'])
def explore():
    return render_template('explore.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    app.run(debug=True)