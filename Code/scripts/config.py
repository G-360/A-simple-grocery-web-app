import os
from dotenv import load_dotenv
from flask import Flask, request
from flask import render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))
basedir, rest = os.path.split(basedir)

load_dotenv(dotenv_path="./scripts/.env")
app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "Database/groceryDB.sqlite3")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
app.secret_key = os.getenv("SECRET_KEY")
app.permanent_session_lifetime = timedelta(days=1)

global fonts 
fonts = os.getenv("FONTS").split(',')

db = SQLAlchemy()
db.init_app(app)
app.app_context().push()
