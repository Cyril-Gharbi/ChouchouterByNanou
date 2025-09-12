from dotenv import load_dotenv
from flask_migrate import Migrate

from app import create_app, db

load_dotenv()

flask_app = create_app()
migrate = Migrate(flask_app, db)

# Expose the app for Gunicorn (CMD: gunicorn -b 0.0.0.0:5000 main:app)
app = flask_app

# run locally
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
