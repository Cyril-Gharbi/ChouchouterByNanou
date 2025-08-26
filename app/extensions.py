# app/extensions.py
import os

from dotenv import load_dotenv
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from pymongo import MongoClient

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
mail = Mail()
mongo_db = None


def init_mongo():
    global mongo_db
    mongo_uri = os.getenv("MONGO_URI")
    mongo_client = MongoClient(mongo_uri)
    mongo_db = mongo_client["chouchouter"]
    return mongo_db
