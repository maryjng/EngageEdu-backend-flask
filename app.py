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

    return 


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
        response_data = resp

        response_data = {
            "user_id": resp.user_id,
            "username": resp.username,
            "email": resp.email,
            "type": resp.type
        }

        return jsonify(response_data), 200

    except IntegrityError as e:
        response_data = {"message", e}
        return response_data, 500

    
if __name__ == '__main__':
    app.run(debug=True)

