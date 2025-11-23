"""Rotas de criação, edição e exclusão de chatbots."""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from extensions import db
from models import BotMessage, Chatbot
from services.chatbot_service import parse_and_validate_tree, persist_tree, serialize_message_tree

bp = Blueprint("builder", __name__)


@bp.route("/builder", methods=["GET", "POST"], endpoint="chatbot_form")
def chatbot_form():
    """Exibe o construtor e cria novos chatbots com árvore de mensagens."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        raw_tree = request.form.get("messages_tree", "")
        has_error = False

        if not name:
            flash("Informe um nome para o chatbot.", "error")
            has_error = True

        message_tree, tree_error = parse_and_validate_tree(raw_tree)
        if tree_error:
            flash(tree_error, "error")
            has_error = True

        if not has_error:
            chatbot = Chatbot(name=name, description=description or None)
            db.session.add(chatbot)
            persist_tree(message_tree, chatbot)
            db.session.commit()
            flash("Chatbot salvo com sucesso!", "success")
            return redirect(url_for("main.list_chatbots"))

    return render_template(
        "form.html",
        form_action=url_for("builder.chatbot_form"),
        initial_tree=[],
        edit_chatbot=None,
    )


@bp.route("/chatbot/<int:bot_id>/edit", methods=["GET", "POST"], endpoint="edit_chatbot")
def edit_chatbot(bot_id):
    """Carrega um chatbot para edição e salva a árvore atualizada."""
    chatbot = Chatbot.query.get_or_404(bot_id)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        raw_tree = request.form.get("messages_tree", "")
        has_error = False

        if not name:
            flash("Informe um nome para o chatbot.", "error")
            has_error = True

        message_tree, tree_error = parse_and_validate_tree(raw_tree)
        if tree_error:
            flash(tree_error, "error")
            has_error = True

        if not has_error:
            chatbot.name = name
            chatbot.description = description or None
            BotMessage.query.filter_by(chatbot_id=chatbot.id).delete()
            persist_tree(message_tree, chatbot)
            db.session.commit()
            flash("Chatbot atualizado com sucesso!", "success")
            return redirect(url_for("builder.chatbot_form"))

    initial_tree = serialize_message_tree(chatbot.root_messages)

    return render_template(
        "form.html",
        edit_chatbot=chatbot,
        initial_tree=initial_tree,
        form_action=url_for("builder.edit_chatbot", bot_id=bot_id),
    )


@bp.post("/chatbot/<int:bot_id>/delete", endpoint="delete_chatbot")
def delete_chatbot(bot_id):
    """Remove um chatbot e suas mensagens."""
    chatbot = Chatbot.query.get_or_404(bot_id)
    db.session.delete(chatbot)
    db.session.commit()
    flash("Chatbot removido com sucesso.", "success")
    return redirect(url_for("main.list_chatbots"))
