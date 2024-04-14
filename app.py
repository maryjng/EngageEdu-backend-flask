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

# with app.app_context():
#     db.create_all()

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
            "course_description": "DSA",
            "professor_id": 7,
            "sections": [
                {
                    "section_id": "1",
                    "section_name": "name",
                    "section_description": "",
                },
                 {
                    "section_id": "2",
                    "section_name": "name 2",
                    "section_description": "",
                },
                 {
                    "section_id": "3",
                    "section_name": "name 3",
                    "section_description": "",
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
                "professor_id": resp.professor_id
            }

            response_data["sections"] = []
            sections_res = db.session.query(Sections).filter_by(course_id=course_id).all()

            for section in sections_res:
                s = {}
                s["section_id"] = section.section_id
                s["section_name"] = section.section_name
                # s["section_description"] = section.section_description
                response_data["sections"].append(s)
                

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
        response_data = {"message": "Course does not exist."}
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

##########################
## PROF SECTION VIEWS ##

@app.route("/course/<course_id>/section/<section_id>", methods=["GET"])
def get_section(course_id, section_id):
    """
    
    """
    try:
        resp = db.session.query(Sections).filter_by(course_id=course_id, section_id=section_id).first()
        if resp:
            response_data = {
                "section_id": resp.section_id,
                "section_name": resp.section_id,
                "course_id": resp.course_id,
                "course_name": resp.course_name,
                # "professor_id": resp.professor_id
            }

            response_data["modules"] = []
            modules_res = db.session.query(Modules).filter_by(section_id=section_id).all()

            for module in modules_res:
                m = {}
                m["module_id"] = module.section_id
                m["module_name"] = module.section_name
                response_data["modules"].append(m)
                
        return jsonify(response_data), 200
    
    except Exception as e:
        print("Exception:", e)
        response_data = {"message": "An error occurred."}
        return jsonify(response_data), 500


@app.route("/course/<course_id>/section", methods=["POST"])
def add_section(course_id):
    """
    data is expected to be { section_name }
    returns { course_id, section_id, section_name } upon success
    """
    try:
        data = request.json

        ##NOTE: section_name starting with 0 will cause an error
        if Courses.get_course(course_id):
            resp = Sections.add_section(
                course_id = course_id,
                section_name = data["section_name"]
            )

            db.session.commit()

            response_data = {
                "course_id": resp.course_id,
                "section_id": resp.section_id,
                "section_name": resp.section_name
            }

            return jsonify(response_data), 200

    except Exception as e:
        print("Exception:", e)
        response_data = {"message": "An error occurred."}
        return jsonify(response_data), 500


@app.route("/course/<course_id>/section/<section_id>", methods=["PATCH"])
def edit_section(course_id, section_id):
    """
    data is expected to be { section_name }
    """
    try:
        data = request.json
        section = db.session.query(Sections).filter_by(course_id=course_id, section_id=section_id).first()

        #primary keys as keys are filtered out in front end to prevent their change
        for key, value in data.items():
            setattr(section, key, value)

        db.session.commit()
        return jsonify({"message": "Section updated successfully"}), 200

    except Exception as e:
        print("Exception:", e)
        response_data = {"message": "An error occurred."}
        return jsonify(response_data), 500
    

@app.route("/course/<course_id>/section/<section_id>", methods=["DELETE"])
def delete_section(course_id, section_id):
    """
    Returns success message upon success.
    """

    try:
        resp = Sections.delete_section(course_id, section_id)
        response_data = {"message": "Section does not exist."}
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


###################################
## PROF MODULE VIEWS ##

@app.route("/course/<course_id>/section/<section_id>/module/<module_id>", methods=["GET"])
def get_module(course_id, section_id, module_id):
    """
    Expects course_id, section_id, module_id
    Returns {
        "course_id": course_id,
        "course_name": course_name,
        "section_id": section_id,
        "section_name": section_name,
        "module_id": module_id,
        "module_name": module_name,
        "professor_id": professor_id,
        "professor_name": professor_name,
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
        ]
    }
    """
    try:
        resp = Modules.get_module(module_id)
        #NEED TO REPLACE PARAMS WHEN DB IS FIXED
        if resp:
            data = db.session.query(
                Users.user_id, 
                Users.username, 
                Courses.course_id, 
                Courses.course_name,
                Sections.section_id,
                Sections.section_name,
                Modules.module_id,
                Modules.module_name
                )
            
            response_data = {
                "course_id": data.course_id,
                "course_name": data.course_name,
                "section_id": data.section_id,
                "section_name": data.section_name,
                "module_id": data.module_id,
                "module_name": data.module_name,
                "professor_id": data.professor_id,
                "professor_name": data.username,
                "module_content": []
            }

            modules_res = db.session.query(ModuleContents).filter_by(module_id=module_id).all()

            for module in modules_res:
                m = {}
                m["module_id"] = module.section_id
                m["module_name"] = module.section_name
                m["video_name"] = module.video_name
                m["video_description"] = module.video_descsription
                m["youtube_embed_url"] = module.youtube_embed_url

                response_data["modules"].append(m)
                
        return jsonify(response_data), 200

    except Exception as e:
        print("Exception:", e)
        response_data = {"message": "An error occurred."}
        return jsonify(response_data), 500


@app.route("/course/<course_id>/section/<section_id>/module", methods=["POST"])
def add_module(course_id, section_id):
    """
    Expects section_name
    Returns { course_id, section_id, module_id, module_name } upon success
    """
    try:
        data = request.json
        response_data = {"message": "course or section id not found"}

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

            return jsonify(response_data), 200
        return jsonify(response_data), 400

    except Exception as e:
        print("Exception:", e)
        response_data = {"message": "An error occurred."}
        return jsonify(response_data), 500


@app.route("/course/<course_id>/section/<section_id>/module/<module_id>", methods=["PATCH"])
def edit_module(course_id, section_id, module_id):
    """
    Expects course_id, section_id, module_id
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
        return jsonify({"message": "Module or session does not exist."}), 400
    

    except Exception as e:
        print("Exception:", e)
        response_data = {"message": "An error occurred."}
        return jsonify(response_data), 500


@app.route("/course/<course_id>/section/<section_id>/module/<module_id>", methods=["DELETE"])
def delete_module(course_id, section_id, module_id):
    """
    Returns success message upon deletion.
    """
    try:
        resp = Modules.delete_module(course_id, section_id, module_id)
        response_data = {"message": "Module does not exist."}
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
#######################



if __name__ == '__main__':
    app.run(debug=True)

