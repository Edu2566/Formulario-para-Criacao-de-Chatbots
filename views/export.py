"""Rotas de exportação de chatbots."""
from flask import Blueprint, make_response, request
from models import Chatbot
from services.chatbot_service import export_pdf, slugify

bp = Blueprint("export", __name__)


@bp.get("/chatbot/<int:bot_id>/map.pdf", endpoint="export_map_pdf")
def export_map_pdf(bot_id):
    """Gera e retorna o PDF do mapa mental de um chatbot específico."""
    chatbot = Chatbot.query.get_or_404(bot_id)
    pdf = export_pdf(chatbot, base_url=request.url_root)

    filename = f"{slugify(chatbot.name)}-mapa-mental.pdf"
    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f'inline; filename="{filename}"'
    return response
