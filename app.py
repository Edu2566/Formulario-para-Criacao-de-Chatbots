"""Aplicação Flask: factory e registro de blueprints."""
import os
from flask import Flask
from extensions import db
from services.chatbot_service import ensure_parent_column
from dotenv import load_dotenv

load_dotenv()


def build_database_uri():
    """Retorna a URL do banco MySQL a partir das variáveis de ambiente."""
    direct_uri = os.getenv("MYSQL_DATABASE_URL")
    if direct_uri:
        return direct_uri

    user = os.getenv("MYSQL_USER", "chatbot")
    password = os.getenv("MYSQL_PASSWORD", "chatbotpass")
    host = os.getenv("MYSQL_HOST", "db")
    port = os.getenv("MYSQL_PORT", "3306")
    db_name = os.getenv("MYSQL_DB", "chatbots")
    return f"mysql://{user}:{password}@{host}:{port}/{db_name}"


def create_app():
    """Cria e configura a aplicação Flask, incluindo DB e blueprints."""
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = build_database_uri()
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
    application.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG") == "1",
    )
