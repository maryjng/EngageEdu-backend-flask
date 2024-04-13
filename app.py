import os
import requests

# from sqlalchemy import join, exc, and_
# from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from flask import Flask, jsonify, request
# from flask_debugtoolbar import DebugToolbarExtension
# from key import API_KEY, SECRET_KEY, USERNAME, PASSWORD


from models import db, connect_db, Users, Courses, Sections, Modules, ModuleContents, Questions, Answers


USERNAME="postgres"
PASSWORD="kitty"
dbname="engageedu"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f"postgresql://{USERNAME}:{PASSWORD}@localhost:5432/{dbname}")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = "SECRET_KEY"

app.debug = True

connect_db(app)

with app.app_context():
    db.create_all()

###################################

@app.route("/")
@app.route("/home", methods=["GET"])
def index():
    return "Hi Ankush"



@app.route("/login", methods=["POST"])
def login():
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
            return jsonify(response_data), 401  # Unauthorized status code

    except Exception as e:
        print("Exception:", e)
        response_data = {"message": "An error occurred."}
        return jsonify(response_data), 500


@app.route("/register", methods=["POST"])
def register():
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

    except Exception as e:
        print("Exception:", e)
        response_data = {"message": "An error occurred."}
        return jsonify(response_data), 500

####################### 
## PROF COURSE VIEWS ##

@app.route("/course/<course_id>", methods=["GET"])
def get_course(course_id):
    """
    Sample response:
    {
        "course_id": 1337,
        "course_name": "DSA",
        "professor_id": 7,
        "sections": {
            "1": "854"
        }
    }
"""
    try:
        resp = Courses.get_course(course_id)
        if resp:
            response_data = {
                "course_id": resp.course_id,
                "course_name": resp.course_name,
                "professor_id": resp.professor_id
            }

            response_data["sections"] = {}
            sections_res = db.session.query(Sections).filter_by(course_id=course_id).all()

            for s in sections_res:
                s_id = s.section_id
                s_name = s.section_name
                response_data["sections"][s_id] = s_name

        return jsonify(response_data), 200
    
    except Exception as e:
        print("Exception:", e)
        response_data = {"message": "An error occurred."}
        return jsonify(response_data), 500


@app.route("/course", methods=["POST"])
def add_course():
    try:
        data = request.json
        resp = Courses.add_course(
            course_name = data["course_name"],
            professor_id = data["professor_id"]
        )

        db.session.commit()

        response_data = {
            "course_id": resp.course_id,
            "course_name": resp.course_name,
            "professor_id": resp.professor_id,
        }

        return jsonify(response_data), 200

    except Exception as e:
        print("Exception:", e)
        response_data = {"message": "An error occurred."}
        return jsonify(response_data), 500


@app.route("/course/<course_id>", methods=["PATCH"])
def edit_course(course_id):
    """ Queries db for course by id. Changes given fields and commits back to db. Errors if course does not exist. Returns the edited course info if successful."""
    try:
        data = request.json
        course = Courses.query.get_or_404(course_id)

        if data["course_id"]: #make sure course_id cannot be changed
            raise Exception("Cannot change course ID.")

        for key, value in data.items():
            setattr(course, key, value)

        db.session.commit()
        return jsonify({"message": "Course updated successfully"}), 200
    
    except Exception as e:
        print("Exception:", e)
        response_data = {"message": "An error occurred."}
        return jsonify(response_data), 500


@app.route("/course/<course_id>", methods=["DELETE"])
def delete_course(course_id):
    """ Returns True if course was deleted. False if not. """
    try:
        resp = Courses.delete_course(course_id)
        if resp:
            response_data = {
                "message": "success"
            }
            return jsonify(response_data), 200
        return jsonify(response_data), 400

    except Exception as e:
        print("Exception:", e)
        response_data = {"message": "An error occurred."}
        return jsonify(response_data), 500        

##
## PROF SECTION VIEWS ##

# @app.route("/course/<course_id>/section", methods=["POST"])
# def add_section(course_id):
#     try:
#         data = request.json

#         if Courses.get_course(course_id):
#             resp = Sections.add_section(
#                 course_id = course_id,
#                 section_name = data["section_name"]
#             )

#             db.session.commit()

#             response_data = {
#                 "course_id": resp.course_id,
#                 "section_id": resp.section_id,
#                 "section_name": resp.section_name
#             }

#             return jsonify(response_data), 200

#     except Exception as e:
#         print("Exception:", e)
#         response_data = {"message": "An error occurred."}
#         return jsonify(response_data), 500



# @app.route("/course/<course_id>/section/<section_id>", methods=["GET"])
# def get_section(course_id, section_id):

##
## PROF MODULE VIEWS ##


##
#######################



if __name__ == '__main__':
    app.run(debug=True)

