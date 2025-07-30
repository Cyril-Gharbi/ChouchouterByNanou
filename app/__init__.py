# flake8: noqa: E402
import os

from dotenv import load_dotenv
from flask_mail import Mail
from flask_migrate import Migrate
from pymongo import MongoClient

from .models import create_app, db

mail = Mail()

load_dotenv()

app = create_app()
mail.init_app(app)

migrate = Migrate(app, db)

# Connect to MongoDB using URI from environment variables
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
mongo_db = client["chouchouter"]

from app.routes import account_routes  # noqa: F401
from app.routes import admin_routes  # noqa: F401
from app.routes import comment_routes  # noqa: F401
from app.routes import main_routes  # noqa: F401
from app.routes import qr_routes  # noqa: F401
from app.routes import reset_password_routes  # noqa: F401
