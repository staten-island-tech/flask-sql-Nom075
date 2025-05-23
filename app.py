from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, Question
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.config['SECRET_KEY'] = 'your_secret_key_here'

db.init_app(app)

ADMIN_PASSWORD = 'Hi'

#Adding questions 

@app.route('/add', methods=['GET', 'POST'])
def add_question():
    if request.method == 'POST':
        question_text = request.form.get('question_text', '').strip()
        option_a = request.form.get('option_a', '').strip()
        option_b = request.form.get('option_b', '').strip()
        option_c = request.form.get('option_c', '').strip()
        option_d = request.form.get('option_d', '').strip()
        correct_answer = request.form.get('correct_answer', '').strip().upper()

        # At least one option must be filled
        options = {'A': option_a, 'B': option_b, 'C': option_c, 'D': option_d}
        if all(not opt for opt in options.values()):
            flash("At least one answer option must be provided.", "danger")
            return render_template('add_question.html')

        # Correct answer must be one of the non-empty options
        if correct_answer not in options or not options[correct_answer]:
            flash("Correct answer must be A, B, C, or D and can not be empty.", "danger")
            return render_template('add_question.html')

        try:
            new_q = Question(
                question_text=question_text,
                option_a=option_a,
                option_b=option_b,
                option_c=option_c,
                option_d=option_d,
                correct_answer=correct_answer
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
    """ random.shuffle(session['question_order']) """    #shuffle questions?
    return redirect(url_for('play_question'))

@app.route('/play', methods=['GET', 'POST'])
def play_question():
    if 'lives' not in session or 'current_q' not in session:
        return redirect(url_for('start_game'))

    question_ids = session['question_order']
    current_index = session['current_q']

    # Check for win condition first
    if current_index >= len(question_ids):
        return render_template('you_win.html')

    question = db.session.get(Question, question_ids[current_index])


    if request.method == 'POST':
        selected = request.form.get('answer')
        if selected == question.correct_answer:
            session['current_q'] += 1
            return redirect(url_for('play_question'))
        else:
            session['lives'] -= 1
            flash('Wrong answer! You lost a life.', 'danger')

            # Check for game over after losing a life
            if session['lives'] <= 0:
                return redirect(url_for('game_over'))

            return redirect(url_for('play_question'))  # Prevent form resubmission on reload

    return render_template(
        'question.html',
        question=question,
        lives=session['lives'],
        current_number=session['current_q'] + 1,  # 1-based display
        total=len(question_ids)
    )





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

@app.route('/game_over')
def game_over():
    return render_template('game_over.html')

@app.route('/restart')
def restart_quiz():
    session.pop('question_index', None)
    session.pop('lives', None)
    session.pop('question_ids', None)
    return redirect(url_for('start_game'))


@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin_authenticated'] = True
            return redirect(url_for('admin'))
        else:
            flash('Incorrect password. Try again.', 'danger')
    return render_template('admin_login.html')



@app.route('/admin')
def admin():
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))

    questions = Question.query.all()
    return render_template('admin.html', questions=questions)


@app.route('/admin-logout')
def admin_logout():
    session.pop('admin_authenticated', None)
    return redirect(url_for('index'))






if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
