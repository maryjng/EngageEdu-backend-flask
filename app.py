import os
import requests

# from sqlalchemy import join, exc, and_
# from sqlalchemy.sql import func
# from sqlalchemy.exc import IntegrityError
from flask import Flask, render_template, flash, redirect, session, g, url_for
# from flask_debugtoolbar import DebugToolbarExtension
# from key import API_KEY, SECRET_KEY, USERNAME, PASSWORD

# from models import db, connect_db, User, Item, Shops, Shops_Item, User_Item

CURR_USER_KEY = "curr_user"

app = Flask(__name__)


@app.route("/")
@app.route("/home", methods=["GET"])
def index():
    return "Hi Ankush"
