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
        try:
            hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')
            user = Users(username=username, email=email, password=hashed_pwd, type=type)
    
            db.session.add(user)
            return user
        except IntegrityError:
            db.session.rollback()
            raise


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
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    description = db.Column(db.String(150), nullable=True)
    professor = db.relationship('Users', backref='courses')

    @classmethod
    def get_all_courses(cls, user_id):
        courses = cls.query.filter_by(user_id=user_id).all()
        return courses

    @classmethod
    def add_course(cls, course_name, user_id, description):
        """ First checks if a course by course_name and user_id exists. If yes, return False. If not, create new course and
        commit to db, then return the new course object.
        """
        course = cls.query.filter_by(course_name=course_name, user_id=user_id).one_or_none()
        if course:
            return False
        new_course = Courses(course_name=course_name, user_id=user_id, description=description)
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
    description = db.Column(db.String(150), nullable=True)

    course = db.relationship('Courses', backref='sections')

    @classmethod
    def get_section(cls, course_id, section_id):
        section = cls.query.filter_by(section_id=section_id, course_id=course_id).first()
        print(section.section_id, section.section_name)
        if section:
            return section
        return False

    @classmethod
    def add_section(cls, section_name, course_id, description):
        #view already calls Course.get_course() to check if course exists
        section = Sections(section_name=section_name, course_id=course_id, description=description)
        db.session.add(section)

        return section
    
    @classmethod
    def delete_section(cls, course_id, section_id):
        """ Returns True on successful deletion. False otherwise. """
        section = cls.query.filter_by(section_id=section_id, course_id=course_id).first()
        if section:
            db.session.delete(section)
            db.session.commit()
            return True
        return False 


class Modules(db.Model):
    __tablename__ = "modules"

    module_id = db.Column(db.Integer, primary_key=True)
    module_name = db.Column(db.String(100), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.section_id'), nullable=False)
    section = db.relationship('Sections', backref='modules')

    @classmethod
    def get_module(cls, module_id):
        module = cls.query.filter_by(module_id=module_id)
        #WHEN DB IS FIXED, REPLACE WITH JOIN STATEMENT
        if module:
            return module
        return False
    
    @classmethod
    def get_all_modules(cls, section_id):
        modules = cls.query.filter_by(section_id=section_id).all()
        return modules

    @classmethod
    def add_module(cls, module_name, section_id):
        module = Modules(module_name=module_name, section_id=section_id)
        db.session.add(module)
        return module
    

    @classmethod
    def delete_module(cls, course_id, section_id, module_id):
        """ Returns True on successful deletion. False otherwise. """
        module = cls.query.filter_by(module_id=module_id, section_id=section_id).first()
        if module:
            db.session.delete(module)
            db.session.commit()
            return True
        return False 
    

class ModuleContents(db.Model):
    __tablename__ = "module_contents"

    content_id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.module_id'), nullable=False)
    module = db.relationship('Modules', backref='contents')
    video_name = db.Column(db.String(100), nullable=False)
    video_description = db.Column(db.Text, nullable=True)
    youtube_embed_url = db.Column(db.String(200), nullable=False)

    @classmethod
    def get_contents(cls, content_id):
        contents = cls.query.filter_by(content_id=content_id).first()
        return contents

    @classmethod
    def get_module_contents(cls, module_id):
        contents = cls.query.filter_by(module_id=module_id).all()
        return contents
    
    @classmethod
    def add_content(cls, module_id, video_name, video_description, youtube_embed_url):
        content = ModuleContents(
            module_id=module_id, 
            video_name=video_name, 
            video_description=video_description, 
            youtube_embed_url=youtube_embed_url
            )
        db.session.add(content)
        return content

    @classmethod
    def delete_content(cls, course_id, section_id, module_id, content_id):
        """ Returns True on successful deletion. False otherwise. """
        content = cls.query.filter_by(module_id=module_id, content_id=content_id).first()
        if content:
            db.session.delete(content)
            db.session.commit()
            return True
        return False 
    

class Questions(db.Model):
    __tablename__ = "questions"

    question_id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.module_id'), nullable=False)
    module = db.relationship('Modules', backref='questions')
    question_text = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    professor = db.relationship('Users', foreign_keys=[created_by])

    @classmethod
    def get_all_questions(cls, course_id, section_id, module_id):
        questions = cls.query.filter_by(module_id=module_id).all()
        return questions

    
    @classmethod
    def get_question(cls, question_id):
        question = cls.query.filter_by(question_id=question_id).first()
        return question
    

    @classmethod
    def add_question(cls, module_id, question_text, created_by):
        question = Questions(
            module_id=module_id, 
            question_text=question_text, 
            created_by=created_by
        )
        db.session.add(question)
        return question
    
    @classmethod
    def delete_question(cls, course_id, section_id, module_id, question_id):
        """ Returns True on successful deletion. False otherwise. """
        question = cls.query.filter_by(module_id=module_id, question_id=question_id).first()
        if question:
            db.session.delete(question)
            db.session.commit()
            return True
        return False 


class Answers(db.Model):
    __tablename__ = "answers"

    answer_id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.question_id'), nullable=False)
    question = db.relationship('Questions', backref='answers')
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    student = db.relationship('Users', backref='answers')
    answer_text = db.Column(db.Text, nullable=False)
    answered_at = db.Column(db.DateTime, nullable=False)

    @classmethod
    def get_all_answers(cls, course_id, section_id, module_id, question_id):
        answers = cls.query.filter_by(question_id=question_id).all()
        return answers
    
    @classmethod
    def add_answer(cls, question_id, user_id, answer_text, answered_at):
        answer = Answers(question_id=question_id, user_id=user_id, answer_text=answer_text, answered_at=answered_at)
        db.session.add(answer)
        return answer

def connect_db(app):
    db.app = app
    db.init_app(app)
