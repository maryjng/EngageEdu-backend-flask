import os
import requests
from datetime import datetime

# from sqlalchemy import join, exc, and_
# from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.exceptions import BadRequest, NotFound
# from flask_debugtoolbar import DebugToolbarExtension
# from key import API_KEY, SECRET_KEY, USERNAME, PASSWORD


from models import db, connect_db, Users, Courses, Sections, Modules, ModuleContents, Questions, Answers


USERNAME="postgres"
PASSWORD="kitty"
dbname="engageedu"

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f"postgresql://{USERNAME}:{PASSWORD}@localhost:5432/{dbname}")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = "SECRET_KEY"

app.debug = True

connect_db(app)

# with app.app_context():
#     db.create_all()

###################################

@app.route("/")
@app.route("/home", methods=["GET"])
def index():
    return "Hi Ankush"


@app.route("/login", methods=["POST"])
def login():
    """ Expects data to be { email, password }
        Returns { user_id, username, email, type }
    """
    try:
        data = request.json

        resp = Users.authenticate(
            email = data["email"],
            password = data["password"]
        )

        if resp:
            response_data = {
            "user_id": resp.user_id,
            "username": resp.username,
            "email": resp.email,
            "type": resp.type
            }
               
            return jsonify(response_data), 200
        
        else:
            response_data = {"message": "Invalid user or password."}
            return jsonify(response_data), 401

    except BadRequest as e:
        # Handle bad request errors
        return jsonify({"message": str(e)}), 400

    except Exception as e:
        # Log the exception details for debugging (not shown to user)
        app.logger.error(f"Exception during login: {e}")
        return jsonify({"message": "An internal error occurred."}), 500


@app.route("/register", methods=["POST"])
def register():
    """
    Expects data to be { username, email, password, type }
    Returns { user_id, username, email, type }
    """
    try:
        data = request.json

        resp = Users.signup(
            username = data["username"],
            email = data["email"],
            password = data["password"],
            type = data["type"]
        )

        db.session.commit()

        response_data = {
            "user_id": resp.user_id,
            "username": resp.username,
            "email": resp.email,
            "type": resp.type
        }

        return jsonify(response_data), 200

    except IntegrityError as e:
        # Handle database integrity errors (e.g., unique constraint violations)
        db.session.rollback()
        return jsonify({"message": "User with this email or username already exists."}), 409

    except BadRequest as e:
        # Handle bad request errors
        return jsonify({"message": str(e)}), 400

    except Exception as e:
        # Log the exception and return a generic error message
        app.logger.error(f"Exception during registration: {e}")
        return jsonify({"message": "An internal error occurred."}), 500

####################### 
## PROF COURSE VIEWS ##
@app.route("/courses", methods=["GET"])
def get_all_courses():
    try:
        user_id = request.args.get('user_id')
        courses = Courses.get_all_courses(user_id)
        response_data = {"courses": []}
    
        for course in courses:
            c = {
                "course_id": course.course_id,
                "course_name": course.course_name,
                "user_id": course.user_id,
                "description": course.description
            }
            response_data["courses"].append(c)
            
         return jsonify(response_data), 200

    except BadRequest as e:
        # Handle bad request errors
        return jsonify({"message": str(e)}), 400

    except Exception as e:
        # Log the exception and return a generic error message
        app.logger.error(f"Exception while getting all courses: {e}")
        return jsonify({"message": "An internal error occurred."}), 500


@app.route("/courses/<course_id>", methods=["GET"])
def get_course(course_id):
    """
        Sample response:
        {
            "course_id": 1337,
            "course_name": "DSA",
            "description": "DSA",
            "user_id": 7,
            "sections": [
                {
                    "section_id": "1",
                    "section_name": "name",
                    "description": "",
                },
                 {
                    "section_id": "2",
                    "section_name": "name 2",
                    "description": "",
                },
                 {
                    "section_id": "3",
                    "section_name": "name 3",
                    "description": "",
                },
            ]
        }
    """
    try:
        resp = Courses.get_course(course_id)
        if resp:
            response_data = {
                "course_id": resp.course_id,
                "course_name": resp.course_name,
                "user_id": resp.user_id,
                "description": resp.description
            }

            response_data["sections"] = []
            sections_res = db.session.query(Sections).filter_by(course_id=course_id).all()

            for section in sections_res:
                s = {}
                s["section_id"] = section.section_id
                s["section_name"] = section.section_name
                s["description"] = section.description
                response_data["sections"].append(s)
                

        return jsonify(response_data), 200
    
    except BadRequest as e:
        # Handle bad request errors
        return jsonify({"message": str(e)}), 400

    except Exception as e:
        # Log the exception and return a generic error message
        app.logger.error(f"Exception while getting course: {e}")
        return jsonify({"message": "An internal error occurred."}), 500
    

@app.route("/courses", methods=["POST"])
def add_course():
    """
    Expects data to have { course_name, user_id, description }
    Returns { course_id, course_name, user_id, description }
    """
    try:
        data = request.json
        resp = Courses.add_course(
            course_name = data["course_name"],
            user_id = data["user_id"],
            description = data["description"]
        )

        db.session.commit()

        response_data = {
            "course_id": resp.course_id,
            "course_name": resp.course_name,
            "user_id": resp.user_id,
            "description": resp.description
        }

        return jsonify(response_data), 201

    except IntegrityError as e:
        # Handle database integrity errors (e.g., unique constraint violations)
        db.session.rollback()
        return jsonify({"message": "Course with this name already exists for the user."}), 409

    except BadRequest as e:
        # Handle bad request errors
        return jsonify({"message": str(e)}), 400

    except Exception as e:
        # Log the exception and return a generic error message
        app.logger.error(f"Exception during adding course: {e}")
        return jsonify({"message": "An internal error occurred."}), 500


@app.route("/courses/<course_id>", methods=["PATCH"])
def edit_course(course_id):
    """ 
    Expects data to have at least one of { course_name, user_id, description }
    Returns success message upon change."""
    try:
        data = request.json
        course = Courses.query.get_or_404(course_id)

        for key, value in data.items():
            setattr(course, key, value)

        db.session.commit()
        return jsonify({"message": "Course updated successfully"}), 200
    
    except BadRequest as e:
        # Handle bad request errors
        return jsonify({"message": str(e)}), 400

    except NotFound:
        # Handle course not found error
        return jsonify({"message": "Course not found"}), 404

    except Exception as e:
        # Log the exception and return a generic error message
        app.logger.error(f"Exception during course edit: {e}")
        return jsonify({"message": "An internal error occurred."}), 500
        

@app.route("/courses/<course_id>", methods=["DELETE"])
def delete_course(course_id):
    """ Returns success message upon deletion. """
    try:
        # Attempt to delete the course
        if Courses.delete_course(course_id):
            return jsonify({"message": "Course deleted successfully"}), 200
        else:
            return jsonify({"message": "Course does not exist"}), 404

    except Exception as e:
        # Log the exception and return a generic error message
        app.logger.error(f"Exception during course deletion: {e}")
        return jsonify({"message": "An internal error occurred."}), 500
        
 
##########################
## PROF SECTION VIEWS ##

@app.route("/courses/<course_id>/sections/<section_id>", methods=["GET"])
def get_section(course_id, section_id):
    """
    Returns example: 
        {
        "section_id": 4,
        "section_name": "section_name",
        "course_id": 3,
        "description": "description",
        "modules": [
            {
                "module_id": 1,
                "module_name": "module"
            },
            {
                "module_id": 2,
                "module_name": "module"
            },
            {
                "module_id": 3,
                "module_name": "test moduleeee"
            }
        ]
        }
    """
    try:
        resp = Sections.get_section(course_id, section_id)
        if resp:
            response_data = {
                "section_id": resp.section_id,
                "section_name": resp.section_name,
                "course_id": resp.course_id,
                "description": resp.description,
            }

            response_data["modules"] = []
            modules_res = db.session.query(Modules).filter_by(section_id=section_id).all()

            for module in modules_res:
                m = {}
                m["module_id"] = module.module_id
                m["module_name"] = module.module_name
                response_data["modules"].append(m)
            
            return jsonify(response_data), 200
            
        else:
            return jsonify({"message": "Section not found"}), 404                        
    
    except Exception as e:
        app.logger.error(f"Exception during section retrieval: {e}")
        return jsonify({"message": "An internal error occurred."}), 500


@app.route("/courses/<course_id>/sections", methods=["POST"])
def add_section(course_id):
    """
    data is expected to be { section_name, description }
    returns { course_id, section_id, section_name } upon success
    """
    try:
        data = request.json

        ##NOTE: section_name starting with 0 will cause an error
        if Courses.get_course(course_id):
            resp = Sections.add_section(
                course_id = course_id,
                section_name = data["section_name"],
                description = data["description"]
            )                

            db.session.commit()

            response_data = {
                "course_id": resp.course_id,
                "section_id": resp.section_id,
                "section_name": resp.section_name,
                "description": resp.description
            }

            return jsonify(response_data), 201
        else:
            return jsonify({"message": "Section not found"}), 404        
    
    except Exception as e:
        app.logger.error(f"Exception during section creation: {e}")
        return jsonify({"message": "An internal error occurred."}), 500


@app.route("/courses/<course_id>/sections/<section_id>", methods=["PATCH"])
def edit_section(course_id, section_id):
    """
    data is expected to be at least one of { section_name, description }
    Returns success message upon change
    """
    try:
        data = request.json
        section = db.session.query(Sections).filter_by(course_id=course_id, section_id=section_id).first()

        if section:
            #primary keys as keys are filtered out in front end to prevent their change
            for key, value in data.items():
                setattr(section, key, value)
    
            db.session.commit()
            return jsonify({"message": "Section updated successfully"}), 200
        else:
            return jsonify({"message": "Section not found"}), 404     

    except Exception as e:
        app.logger.error(f"Exception during section edit: {e}")
        return jsonify({"message": "An internal error occurred."}), 500
    

@app.route("/courses/<course_id>/sections/<section_id>", methods=["DELETE"])
def delete_section(course_id, section_id):
    """
    Returns success message upon deletion.
    """

    try:
        resp = Sections.delete_section(course_id, section_id)
        if resp:
            response_data = {
                "message": "success"
            }
            return jsonify(response_data), 200
        else:
            return jsonify({"message": "Section not found"}), 404 

    except Exception as e:
        app.logger.error(f"Exception during section deletion: {e}")
        return jsonify({"message": "An internal error occurred."}), 500


###################################
## PROF MODULE VIEWS ##

@app.route("/courses/<course_id>/sections/<section_id>/modules", methods=["GET"])
def get_modules(course_id, section_id):
    try:
        modules = Modules.get_all_modules(section_id=section_id)
        response_data = {"modules": []}

        if modules:
            for module in modules:
                m = {
                    "module_id": module.module_id,
                    "module_name": module.module_name,
                    "section_id": module.section_id
                }
                response_data["modules"].append(m)
            
            return jsonify(response_data), 200
        else:
            return jsonify({"message": "Section not found"}), 404 
            
    except Exception as e:
        app.logger.error(f"Exception during section deletion: {e}")
        return jsonify({"message": "An internal error occurred."}), 500
        

@app.route("/courses/<course_id>/sections/<section_id>/modules/<module_id>", methods=["GET"])
def get_module(course_id, section_id, module_id):
    """
    Returns {
        "module_id": module_id,
        "module_content": [
            {
                "content_id": content_id,
                "video_name": video_name,
                "video_description": video_description,
                "youtube_embed_url": youtube_embed_url
            },
            {
                ...
            }
        ],

        "questions": [
            {
                "question_id": question_id,
                "question_text": question_text,
                "created_by": created_by
            },
            {
                ...
            }
        ]
    }
    """
    try:
        resp = Modules.get_module(module_id)
        #NEED TO REPLACE PARAMS WHEN DB IS FIXED
        if resp:
            # data = ModuleContents.get_module_contents(module_id)
            response_data = {
                "module_id": module_id,
                "module_content": [],
                "questions": []
                }

            modules_res = db.session.query(ModuleContents).filter_by(module_id=module_id).all()

            for module in modules_res:
                m = {}
                m["content_id"] = module.content_id
                m["video_name"] = module.video_name
                m["video_description"] = module.video_description
                m["youtube_embed_url"] = module.youtube_embed_url

                response_data["module_content"].append(m)
            
            questions_res = db.session.query(Questions).filter_by(module_id=module_id).all()

            for question in questions_res:
                q = {}
                q["question_id"] = question.question_id
                q["question_text"] = question.question_text
                q["created_by"] = question.created_by

                response_data["questions"].append(q)
                
            return jsonify(response_data), 200

        else:
            return jsonify({"message": "Module not found"}), 404 

    except Exception as e:
        app.logger.error(f"Exception during module retrieval: {e}")
        return jsonify({"message": "An internal error occurred."}), 500


@app.route("/courses/<course_id>/sections/<section_id>/modules", methods=["POST"])
def add_module(course_id, section_id):
    """
    Expects { section_name }
    Returns { course_id, section_id, module_id, module_name } upon success
    """
    try:
        data = request.json

        if Sections.get_section(course_id, section_id):
            #Get section given course and section ids
            resp = Modules.add_module(
                section_id = section_id,
                module_name = data["module_name"]
            )

            db.session.commit()

            response_data = {
                "course_id": course_id,
                "section_id": section_id,
                "module_id": resp.module_id,
                "module_name": resp.module_name
            }

            return jsonify(response_data), 201
            
        else:
            return jsonify({"message": "Section not found"}), 404

    except Exception as e:
        app.logger.error(f"Exception during module retrieval: {e}")
        return jsonify({"message": "An internal error occurred."}), 500



@app.route("/courses/<course_id>/sections/<section_id>/modules/<module_id>", methods=["PATCH"])
def edit_module(course_id, section_id, module_id):
    """
    Expects { module_name }
    Returns success message upon successful update
    """
    try:
        data = request.json
        module = db.session.query(Modules).filter_by(module_id=module_id, section_id=section_id).first()

        if module:
            #primary keys as keys are filtered out in front end to prevent their change
            for key, value in data.items():
                setattr(module, key, value)

            db.session.commit()

            return jsonify({"message": "Section updated successfully"}), 200
        else:
            return jsonify({"message": "Section or module not found"}), 404

    except Exception as e:
        app.logger.error(f"Exception during module update: {e}")
        return jsonify({"message": "An internal error occurred."}), 500


@app.route("/courses/<course_id>/sections/<section_id>/modules/<module_id>", methods=["DELETE"])
def delete_module(course_id, section_id, module_id):
    """
    Returns success message upon deletion.
    """
    try:
        resp = Modules.delete_module(course_id, section_id, module_id)
        if resp:
            response_data = {
                "message": "success"
            }
            return jsonify(response_data), 200
        else:
            return jsonify({"message": "Section or module not found"}), 404

    except Exception as e:
        app.logger.error(f"Exception during module update: {e}")
        return jsonify({"message": "An internal error occurred."}), 500


#############################
## PROF MODULE_CONTENTS VIEWS
@app.route("/courses/<course_id>/sections/<section_id>/modules/<module_id>/contents/<content_id>", methods=["GET"])
def get_content(course_id, section_id, module_id, content_id):
    """
    Returns { content_id, module_id, video_name, video_description, youtube_embed_url } for the content_id
    """
    try:
        content = ModuleContents.get_contents(content_id)
        if content:
            response_data = {
                "content_id": content.content_id,
                "module_id": content.module_id,
                "video_name": content.video_name,
                "video_description": content.video_description,
                "youtube_embed_url": content.youtube_embed_url
            }
    
            return jsonify(response_data), 200
        else:
            return jsonify({"message": "Content not found"}), 404

    except Exception as e:
        app.logger.error(f"Exception during content retrieval: {e}")
        return jsonify({"message": "An internal error occurred."}), 500


@app.route("/courses/<course_id>/sections/<section_id>/modules/<module_id>/contents", methods=["POST"])
def add_content(course_id, section_id, module_id):
    """
    Expects data { video_name, video_description, youtube_embed_url }
    Returns { content_id, video_name, video_description, youtube_embed_url }
    """
    try:
        data = request.json

        resp = ModuleContents.add_content(
            module_id=module_id, 
            video_name=data["video_name"], 
            video_description=data["video_description"], 
            youtube_embed_url=data["youtube_embed_url"]
        )

        if resp:
            db.session.commit()
    
            response_data = {
                "content_id": resp.content_id,
                "video_name": resp.video_name,
                "video_description": resp.video_description,
                "youtube_embed_url": resp.youtube_embed_url
            }
    
            return jsonify(response_data), 201
        else:
            return jsonify({"message": "Module not found"}), 404
            
    except Exception as e:
        app.logger.error(f"Exception during content creation: {e}")
        return jsonify({"message": "An internal error occurred."}), 500


@app.route("/courses/<course_id>/sections/<section_id>/modules/<module_id>/contents/<content_id>", methods=["PATCH"])
def edit_content(course_id, section_id, module_id, content_id):
    """
    Expects data to at least have one of { video_name, video_description, youtube_embed_url }
    Returns success message upon change
    """
    try:
        data = request.json
        content = db.session.query(ModuleContents).filter_by(module_id=module_id, content_id=content_id).first()

        if content:
            for key, value in data.items():
                setattr(content, key, value)

            db.session.commit()

            return jsonify({"message": "Section updated successfully"}), 200
        return jsonify({"message": "Content does not exist."}), 404
    
    except Exception as e:
        app.logger.error(f"Exception during content update: {e}")
        return jsonify({"message": "An internal error occurred."}), 500


@app.route("/courses/<course_id>/sections/<section_id>/modules/<module_id>/contents/<content_id>", methods=["DELETE"])
def delete_content(course_id, section_id, module_id, content_id):
    """
    Returns success message upon deletion.
    """
    try:
        resp = ModuleContents.delete_content(course_id, section_id, module_id, content_id)
        if resp:
            response_data = {
                "message": "success"
            }
            return jsonify(response_data), 200
        else:
            return jsonify({"message": "Content does not exist."}), 404

    except Exception as e:
        app.logger.error(f"Exception during content deletion: {e}")
        return jsonify({"message": "An internal error occurred."}), 500  


#######################
## PROF QUESTIONS VIEWS

@app.route("/courses/<course_id>/sections/<section_id>/modules/<module_id>/questions/<question_id>", methods=["GET"])
def get_question(course_id, section_id, module_id, question_id):
    """
    Returns { 
        question_id, 
        module_id, 
        question_text, 
        created_by,
        "answers": [
            {
                "answer_id": answer_id,
                "student_id": user_id,
                "answer_text": answer_text,
                "answered_at": answered_at
            },
            { ... }
        ]
    }
    """
    try:
        question = Questions.get_question(question_id)

        answers = Answers.get_all_answers(course_id, section_id, module_id, question_id)

        if answers:
            answer_dicts = [answer.to_dict() for answer in answers]
    
            response_data = {
                "question_id": question_id,
                "module_id": question.module_id,
                "question_text": question.question_text,
                "created_by": question.created_by,
                "answers": answer_dicts
            }
    
            return jsonify(response_data), 200
        else:
            return jsonify({"message": "Question does not exist."}), 404

    except Exception as e:
        app.logger.error(f"Exception during question retrieval: {e}")
        return jsonify({"message": "An internal error occurred."}), 500  


@app.route("/courses/<course_id>/sections/<section_id>/modules/<module_id>/questions", methods=["POST"])
def add_question(course_id, section_id, module_id):
    """
    Expects data to have { question_text, created_by }, where created_by is a valid user_id
    Returns { module_id, question_text, created_by }
    """
    try:
        data = request.json
        response_data = {"message": "Module not found"}

        resp = Questions.add_question(
            module_id=module_id, 
            question_text=data["question_text"], 
            created_by=data["created_by"]
        )

        if resp:
            db.session.commit()
    
            response_data = {
                "module_id": resp.module_id,
                "question_text": resp.question_text,
                "created_by": resp.created_by
            }
    
            return jsonify(response_data), 201
        else:
            return jsonify({"message": "Module does not exist."}), 404
            
    except Exception as e:
        app.logger.error(f"Exception during question creation: {e}")
        return jsonify({"message": "An internal error occurred."}), 500  


@app.route("/courses/<course_id>/sections/<section_id>/modules/<module_id>/questions/<question_id>", methods=["PATCH"])
def edit_question(course_id, section_id, module_id, question_id):
    """
    Expects data to at least have one of { question_text, created_by }
    Returns success message upon change
    """
    try:
        data = request.json
        question = db.session.query(Questions).filter_by(module_id=module_id, question_id=question_id).first()

        if question:
            for key, value in data.items():
                setattr(question, key, value)

            db.session.commit()

            return jsonify({"message": "Section updated successfully"}), 200
        return jsonify({"message": "Content does not exist."}), 404
    

    except Exception as e:
        app.logger.error(f"Exception during content update: {e}")
        return jsonify({"message": "An internal error occurred."}), 500  


@app.route("/courses/<course_id>/sections/<section_id>/modules/<module_id>/questions/<question_id>", methods=["DELETE"])
def delete_question(course_id, section_id, module_id, question_id):   
    """
    Returns success message upon deletion.
    """
    try:
        resp = Questions.delete_question(course_id, section_id, module_id, question_id)
        if resp:
            response_data = {
                "message": "success"
            }
            return jsonify(response_data), 200
        else:
            return jsonify({"message": "Question does not exist."}), 404

    except Exception as e:
        app.logger.error(f"Exception during question deletion: {e}")
        return jsonify({"message": "An internal error occurred."}), 500       


########################
## PROF ANSWERS VIEWS

@app.route("/courses/<course_id>/sections/<section_id>/modules/<module_id>/questions/<question_id>/answers/<answer_id>", methods=["GET"])
def get_answer(course_id, section_id, module_id, question_id, answer_id):
    try:
        #TODO
        pass
    except Exception as e:
        app.logger.error(f"Exception during answer retrieval: {e}")
        return jsonify({"message": "An internal error occurred."}), 500       
    
    
@app.route("/courses/<course_id>/sections/<section_id>/modules/<module_id>/questions/<question_id>/answers", methods=["POST"])
def add_answer(course_id, section_id, module_id, question_id):
    try:
        data = request.json

        resp = Answers.add_answer(
            question_id=question_id, 
            user_id=data["user_id"],
            answer_text=data["answer_text"],
            answered_at=datetime.now()
            # answered_at=data["answered_at"]
        )

        if resp:
            db.session.commit()
    
            response_data = {
                "question_id": question_id,
                "user_id": resp.user_id,
                "answer_text": resp.answer_text,
                "answered_at": resp.answered_at
            }
    
            return jsonify(response_data), 201
        else:
            return jsonify({"message": "Question does not exist."}), 404
            
    except Exception as e:
        app.logger.error(f"Exception during answer creation: {e}")
        return jsonify({"message": "An internal error occurred."}), 500       

##
#######################



if __name__ == '__main__':
    app.run(debug=True)

