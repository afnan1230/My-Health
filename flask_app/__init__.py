from flask import Flask, redirect, url_for, render_template,request,session,flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = '1cc3c2e48b741275bce74ac0ba1da6e0'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
from flask_app import routes