from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, Question
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.config['SECRET_KEY'] = 'your_secret_key_here'

db.init_app(app)

#Adding questions 

@app.route('/add', methods=['GET', 'POST'])
def add_question():
    if request.method == 'POST':
        try:
            new_q = Question(
                question_text=request.form['question_text'],
                option_a=request.form['option_a'],
                option_b=request.form['option_b'],
                option_c=request.form['option_c'],
                option_d=request.form['option_d'],
                correct_answer=request.form['correct_answer'].upper()
            )
            db.session.add(new_q)
            db.session.commit()
            flash("Question added successfully!", "success")
            return redirect(url_for('admin'))
        except Exception as e:
            flash(f"Error: {e}", "danger")
    return render_template('add_question.html')

#Read the questions

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start')
def start_game():
    session['lives'] = 3
    session['current_q'] = 0
    session['question_order'] = [q.id for q in Question.query.all()]
    random.shuffle(session['question_order'])
    return redirect(url_for('play_question'))

@app.route('/play', methods=['GET', 'POST'])
def play_question():
    if 'lives' not in session or 'current_q' not in session:
        return redirect(url_for('start_game'))

    if session['lives'] <= 0:
        return render_template('game_over.html')

    question_ids = session['question_order']
    current_index = session['current_q']

    if current_index >= len(question_ids):
        return render_template('you_win.html')

    question = Question.query.get(question_ids[current_index])

    if request.method == 'POST':
        selected = request.form.get('answer')
        if selected == question.correct_answer:
            session['current_q'] += 1
            return redirect(url_for('play_question'))
        else:
            session['lives'] -= 1
            flash('Wrong answer! You lost a life.', 'danger')

    return render_template('question.html', question=question, lives=session['lives'])


#Updating and changing the questions

@app.route('/edit/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)
    if request.method == 'POST':
        question.question_text = request.form['question_text']
        question.option_a = request.form['option_a']
        question.option_b = request.form['option_b']
        question.option_c = request.form['option_c']
        question.option_d = request.form['option_d']
        question.correct_answer = request.form['correct_answer'].upper()
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('edit_questions.html', question=question)


#Deleting questions

@app.route('/delete/<int:question_id>')
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('admin'))

#Admin dashboard

@app.route('/admin')
def admin():
    questions = Question.query.all()
    return render_template('admin.html', questions=questions)










if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
