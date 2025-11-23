"""Extensões compartilhadas da aplicação (instâncias globais)."""
from flask_sqlalchemy import SQLAlchemy

# Único ponto de criação do db para ser importado pelos modelos e pela factory.
db = SQLAlchemy()
