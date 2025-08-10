from flask import Flask, jsonify, send_from_directory
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from database import db
import os

def create_app():
    app = Flask(__name__, static_folder='../static', template_folder='../templates')

    # Configuration de la base de données
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///promotion_manager.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Configuration de JWT
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "super-secret-key")

    # Initialisation des extensions
    db.init_app(app)
    jwt = JWTManager(app)
    CORS(app)

    # Importation des modèles
    from models.user import User
    from models.campaign import Campaign
    from models.promotion_data import PromotionData

    # Création des tables de la base de données
    with app.app_context():
        db.create_all()

    # Enregistrement des blueprints (routes API) - DEPLACE ICI
    from routes.auth import auth_bp
    from routes.campaign import campaign_bp
    from routes.promotion_data import promotion_data_bp
    from routes.user import user_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(campaign_bp)
    app.register_blueprint(promotion_data_bp)
    app.register_blueprint(user_bp)

    # Route pour servir le frontend React
    @app.route("/")
    def serve_index():
        return send_from_directory(app.template_folder, "index.html")

    @app.route("/<path:path>")
    def serve_static_files(path):
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.template_folder, "index.html")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0")
