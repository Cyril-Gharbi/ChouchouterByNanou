from flask import Flask
from flask_migrate import Migrate
from dotenv import load_dotenv
from pymongo import MongoClient
import os
from flask_mail import Mail

mail = Mail()

from .models import db, create_app

load_dotenv()

app = create_app()
mail.init_app(app)

migrate = Migrate(app, db)

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
mongo_db = client["chouchouter"]

from . import routes