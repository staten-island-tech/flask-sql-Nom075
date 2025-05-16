from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Question

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.config['SECRET_KEY'] = 'your-secret-key'
db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()

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

@app.route('/quiz')
def quiz():
    questions = Question.query.all()
    return render_template('quiz.html', questions=questions)

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
    return render_template('edit_question.html', question=question)


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
