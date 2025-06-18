from flask import Flask
from flask_migrate import Migrate
from dotenv import load_dotenv
from pymongo import MongoClient
import os
from flask_mail import Mail
mail = Mail()

load_dotenv()

from .models import db, create_app, login_manager


app = create_app()
mail.init_app(app)

migrate = Migrate(app, db)

# Connect to MongoDB using URI from environment variables
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
mongo_db = client["chouchouter"]

from app.routes import main_routes, admin_routes, comment_routes, account_routes, qr_routes, reset_password_routes