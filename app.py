from dotenv import load_dotenv
from flask_migrate import Migrate

import app.routes.account_routes as account_routes
import app.routes.admin_routes as admin_routes
import app.routes.comment_routes as comment_routes
import app.routes.main_routes as main_routes
import app.routes.qr_routes as qr_routes
import app.routes.reset_password_routes as reset_password_routes
from app import create_app
from app.extensions import db, init_mongo, mail

load_dotenv()

# Création de l'application Flask
flask_app = create_app()

# Déclaration des extensions spécifiques
mail.init_app(flask_app)
migrate = Migrate(flask_app, db)
mongo_db = init_mongo()


main_routes.init_routes(flask_app, mongo_db)
account_routes.init_routes(flask_app)
admin_routes.init_routes(flask_app, mongo_db)
comment_routes.init_routes(flask_app)
qr_routes.init_routes(flask_app)
reset_password_routes.init_routes(flask_app)

# Point d'entrée
if __name__ == "__main__":
    flask_app.run(debug=True)
