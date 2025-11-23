"""Regras de negócio e utilitários para chatbots e mensagens."""
import json
import re
from sqlalchemy import inspect, text
from sqlalchemy.orm import joinedload
from weasyprint import HTML
from extensions import db
from models import BotMessage, Chatbot


def ensure_parent_column():
    """Garante que a coluna parent_id existe (migração leve para bases antigas)."""
    inspector = inspect(db.engine)
    columns = [col["name"] for col in inspector.get_columns("bot_messages")]
    if "parent_id" not in columns:
        with db.engine.begin() as connection:
            connection.execute(text("ALTER TABLE bot_messages ADD COLUMN parent_id INTEGER"))


def serialize_message_tree(messages):
    """Converte uma lista de mensagens em dicionários aninhados (id, content, children)."""
    serialized = []
    for message in messages:
        serialized.append(
            {
                "id": message.id,
                "content": message.content,
                "children": serialize_message_tree(message.children),
            }
        )
    return serialized


def parse_and_validate_tree(raw_tree):
    """Faz parse do JSON de árvore e valida conteúdos e estrutura."""
    try:
        tree = json.loads(raw_tree) if raw_tree else []
    except json.JSONDecodeError:
        return [], "Não foi possível ler as mensagens enviadas. Tente novamente."

    def tree_is_valid(nodes):
        """Valida recursivamente se todos os nós possuem conteúdo e filhos válidos."""
        if not nodes:
            return False
        for node in nodes:
            if not isinstance(node, dict):
                return False
            content = (node.get("content") or "").strip()
            if not content:
                return False
            children = node.get("children") or []
            if children and not tree_is_valid(children):
                return False
        return True

    if not tree:
        return [], "Adicione pelo menos uma mensagem e subopções antes de salvar."
    if not tree_is_valid(tree):
        return [], "Preencha todas as mensagens e subopções antes de salvar."
    
    print(tree)

    return tree, None


def persist_tree(nodes, chatbot, parent=None):
    """Persiste recursivamente a árvore de mensagens mantendo a ordem e hierarquia."""
    for idx, node in enumerate(nodes):
        message = BotMessage(
            content=node["content"].strip(),
            order=idx,
            chatbot=chatbot,
            parent=parent,
        )
        db.session.add(message)
        children = node.get("children") or []
        if children:
            persist_tree(children, chatbot, parent=message)


def fetch_chatbots():
    """Busca chatbots com suas mensagens carregadas em ordem (incluindo filhos)."""
    return (
        Chatbot.query.options(joinedload(Chatbot.messages).joinedload(BotMessage.children))
        .order_by(Chatbot.created_at.desc())
        .all()
    )


def slugify(value):
    """Normaliza um texto para ser usado em nomes de arquivo amigáveis."""
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9-]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or "chatbot"


def export_pdf(chatbot, base_url):
    """Gera o PDF do mapa mental a partir do template HTML."""
    html = HTML(string=chatbot_to_html(chatbot), base_url=base_url)
    return html.write_pdf()


def chatbot_to_html(chatbot):
    """Renderiza o HTML do mapa mental para um chatbot."""
    from flask import render_template

    return render_template("map_pdf.html", chatbot=chatbot)
