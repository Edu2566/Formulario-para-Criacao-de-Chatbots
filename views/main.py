"""Rotas principais: home, lista e mapas mentais."""
from flask import Blueprint, redirect, render_template, url_for
from services.chatbot_service import fetch_chatbots

bp = Blueprint("main", __name__)


@bp.route("/", endpoint="home")
def home():
    """Redireciona para a lista de chatbots."""
    return redirect(url_for("main.list_chatbots"))


@bp.route("/chatbots", endpoint="list_chatbots")
def list_chatbots():
    """Lista chatbots com visão escrita das mensagens."""
    chatbots = fetch_chatbots()
    return render_template("list.html", chatbots=chatbots)


@bp.route("/maps", endpoint="maps_view")
def maps_view():
    """Exibe os mapas mentais de todos os chatbots."""
    chatbots = fetch_chatbots()
    return render_template("maps.html", chatbots=chatbots)
