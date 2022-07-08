from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_marshmallow import Marshmallow
from flask_restful import (
    Api,
    Resource
)
from password_hashing import Hash
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_user,
    logout_user,
    login_required
)


app = Flask(__name__)
app.secret_key = 'secret-key'
marshmallow = Marshmallow(app)
api = Api(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager()
login_manager.init_app(app)

local = False
if local:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:12345678@127.0.0.1/forumDB'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://bf7297db16c9e8:b6803a4e@us-cdbr-east-06.cleardb.net/heroku_d45554ec1356827'

db = SQLAlchemy(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(1500), nullable=False)
    created_at = db.Column(db.String(12), nullable=False)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    user = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.String(12), nullable=False)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Integer, nullable=False)
    user = db.Column(db.Integer, nullable=False)
    text = db.Column(db.String(1500), nullable=False)
    created_at = db.Column(db.String(12), nullable=False)

# serializer for question Api


class QuestionSchema(marshmallow.Schema):
    class Meta:
        fields = ("id", "text", "user", "created_at")
        model = Question


questions_schema = QuestionSchema(many=True)


# question api endpoint


class QuestionListResource(Resource):
    def get(self):
        questions = Question.query.all()
        return questions_schema.dump(questions)


api.add_resource(QuestionListResource, '/questions_api')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    questions = Question.query\
        .join(User, User.id == Question.user)\
        .add_columns(Question.id, User.username, Question.text, Question.created_at).all()
    return render_template('index.html', questions=questions)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    try:
        if request.method == 'POST':
            username = request.values.get('username')
            password = Hash.hash_password(request.values.get('password'))
            created_at = datetime.now().date()
            user = User.query.filter_by(username=username).first()
            if not user:
                user = User(username=username, password=password,
                            created_at=created_at)
                db.session.add(user)
                db.session.commit()
                flash('User Added succesfully', 'info')
            else:
                flash('User Already Exists', 'error')
    except Exception as error:
        print(error)
        flash('Something went wrong please try again later', 'error')

    return redirect('/')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    try:
        if request.method == 'POST':
            username = request.values.get('username')
            password = request.values.get('password')
            user = User.query.filter_by(username=username).first()
            if user and Hash.verify_password(user.password, password):
                login_user(user)
            else:
                flash('Username or password is incorrect', 'error')
    except Exception as error:
        print(error)
        flash('Something went wrong please try again later', 'error')

    return redirect('/')


@app.route('/logout')
@login_required
def logout():
    try:
        logout_user()
    except Exception as error:
        print(error)
    return redirect('/')


@app.route('/create_question', methods=['GET', 'POST'])
@login_required
def create_topic():
    try:
        if request.method == 'POST':
            question = request.form.get('topicName')
            user_id = current_user.id
            current_date = datetime.now().date()
            new_question = Question(
                text=question, user=user_id, created_at=current_date)
            db.session.add(new_question)
            db.session.commit()
    except Exception as error:
        print(error)
    return redirect('/')


@app.route('/comments/<int:question_id>')
def comments(question_id=None):
    try:
        comments = Comment.query\
            .join(User, User.id == Comment.user)\
            .add_columns(Comment.id, Comment.question, Comment.user, Comment.text, Comment.created_at, User.username)\
            .filter(Comment.question == question_id).all()
        question = Question.query.filter_by(id=question_id).first()
    except Exception as error:
        print(error)
        return redirect('/')
    return render_template('comments.html', comments=comments, question=question)


@app.route('/create_comment/<int:question_id>', methods=['POST'])
@login_required
def create_comment(question_id):
    try:
        if request.method == 'POST':
            comment_text = request.form.get('claim_text')
            current_date = datetime.now().date()
            new_comment = Comment(question=question_id, user=current_user.id,
                                  text=comment_text, created_at=current_date)
            db.session.add(new_comment)
            db.session.commit()
    except Exception as error:
        print(error)
        flash('Something went wrong')
        return redirect('/')
    return redirect(f'/comments/{question_id}')

if __name__ == '__main__':
    app.run()