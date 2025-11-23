"""Aplicação Flask: factory e registro de blueprints."""
import os
from flask import Flask
from extensions import db
from services.chatbot_service import ensure_parent_column
from dotenv import load_dotenv

load_dotenv()

def create_app():
    """Cria e configura a aplicação Flask, incluindo DB e blueprints."""
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("MYSQL_DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()
        ensure_parent_column()

    from views import builder, export, main

    app.register_blueprint(main.bp)
    app.register_blueprint(builder.bp)
    app.register_blueprint(export.bp)

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(debug=True)
