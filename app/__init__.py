from flask import Flask
from flask_session import Session
import os

app = Flask(__name__)
app.config.from_pyfile("DEFAULT_SETTINGS.cfg")

SESSION_TYPE = 'redis'
app.config.from_object(__name__)
Session(app)

# for flash requests
app.secret_key = app.config['SECRET_KEY']

from app import db
from app import views
from app import forms
from app import gpt
from app import src
