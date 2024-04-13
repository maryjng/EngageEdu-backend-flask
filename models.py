from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()
    

class Users(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True) #LOG IN WITH EMAIL AND PASSWORD (username not unique)
    password = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)

    @classmethod
    def signup(cls, username, email, password, type):
        """Sign up user. Hashes password and adds user to system."""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')
        user = Users(username=username, email=email, password=hashed_pwd, type=type)

        db.session.add(user)
        return user


    @classmethod
    def authenticate(cls, email, password):
        """Find user with `email` and `password`. searches for an email whose password hash matches this password
        and, if it finds such an email, returns that email object.
        If can't find matching email (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(email=email).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class Courses(db.Model):
    __tablename__ = "courses"

    course_id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    professor = db.relationship('Users', backref='courses')

    @classmethod
    def add_course(cls, course_name, professor_id):
        """ First checks if a course by course_name and professor_id exists. If yes, return False. If not, create new course and
        commit to db, then return the new course object.
        """
        course = cls.query.filter_by(course_name=course_name, professor_id=professor_id).one_or_none()
        if course:
            return False
        new_course = Courses(course_name=course_name, professor_id=professor_id)
        db.session.add(new_course)

        return new_course

    @classmethod
    def get_course(cls, course_id):
        """ Returns the queried course if exists. Otherwise returns False. """
        course = cls.query.filter_by(course_id=course_id).first()
        if course:
            return course
        return False
    
    @classmethod
    def delete_course(cls, course_id):
        """ Returns True on successful deletion. False otherwise. """
        course = cls.query.filter_by(course_id=course_id).first()
        if course:
            db.session.delete(course)
            db.session.commit()
            return True
        return False 


class Sections(db.Model):
    __tablename__ = "sections"

    section_id = db.Column(db.Integer, primary_key=True)
    section_name = db.Column(db.String(100), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'), nullable=False)
    course = db.relationship('Courses', backref='sections')


class Modules(db.Model):
    __tablename__ = "modules"

    module_id = db.Column(db.Integer, primary_key=True)
    module_name = db.Column(db.String(100), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.section_id'), nullable=False)
    section = db.relationship('Sections', backref='modules')


class ModuleContents(db.Model):
    __tablename__ = "module_contents"

    content_id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.module_id'), nullable=False)
    module = db.relationship('Modules', backref='contents')
    video_name = db.Column(db.String(100), nullable=False)
    video_description = db.Column(db.Text, nullable=True)
    youtube_embed_url = db.Column(db.String(200), nullable=False)


class Questions(db.Model):
    __tablename__ = "questions"

    question_id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.module_id'), nullable=False)
    module = db.relationship('Modules', backref='questions')
    question_text = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    professor = db.relationship('Users', foreign_keys=[created_by])


class Answers(db.Model):
    __tablename__ = "answers"

    answer_id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.question_id'), nullable=False)
    question = db.relationship('Questions', backref='answers')
    student_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    student = db.relationship('Users', backref='answers')
    answer_text = db.Column(db.Text, nullable=False)
    answered_at = db.Column(db.DateTime, nullable=False)


def connect_db(app):
    db.app = app
    db.init_app(app)