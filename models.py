"""Modelos de domínio dos chatbots e mensagens."""
from sqlalchemy import func
from sqlalchemy.orm import relationship
from extensions import db


class Chatbot(db.Model):
    """Entidade de chatbot com metadados e relação de mensagens."""

    __tablename__ = "chatbots"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, server_default=func.now())

    messages = relationship(
        "BotMessage",
        backref="chatbot",
        cascade="all, delete-orphan",
        order_by="BotMessage.order.asc()",
        lazy="selectin",
        overlaps="parent,children",
    )

    @property
    def root_messages(self):
        """Retorna apenas as mensagens raiz, ordenadas pela posição."""
        roots = [message for message in self.messages if message.parent_id is None]
        return sorted(roots, key=lambda msg: msg.order)


class BotMessage(db.Model):
    """Mensagem do chatbot, podendo ter submensagens (filhos)."""

    __tablename__ = "bot_messages"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, nullable=False, default=0)
    chatbot_id = db.Column(db.Integer, db.ForeignKey("chatbots.id"), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("bot_messages.id"), nullable=True)

    children = relationship(
        "BotMessage",
        backref=db.backref("parent", remote_side=[id]),
        cascade="all, delete-orphan",
        order_by="BotMessage.order.asc()",
        single_parent=True,
        lazy="selectin",
        overlaps="chatbot,messages",
    )
