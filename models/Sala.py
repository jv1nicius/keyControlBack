from helpers.database import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Text
from marshmallow import Schema, fields, validate, ValidationError
from flask_restful import fields as flaskFields


sala_fields = {
    'sala_id': flaskFields.Integer,
    'sala_nome': flaskFields.String,
    'chave_nome': flaskFields.String
}


def validate_positive(value):
    if value < 0:
        raise ValidationError("O valor deve ser um número inteiro não negativo.")


class Sala(db.Model):
    __tablename__ = "sala"

    sala_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sala_nome: Mapped[str] = mapped_column(Text, nullable=False)
    chave_nome: Mapped[str] = mapped_column(Text, nullable=False)

    reserva = relationship("Reserva", back_populates="sala")


class SalaSchema(Schema):
    sala_id = fields.Int(dump_only=True)
    sala_nome = fields.Str(
        required=True, 
        validate=validate.Length(min=3, max=255),
        error_messages={
            "required": "O campo sala_nome é obrigatório.",
            "null": "O campo sala_nome não pode ser nulo.",
            "validator_failed": "O campo sala_nome deve ter entre 3 e 255 caracteres."
        }
    )
    chave_nome = fields.Str(
        required=True, 
        validate=validate.Length(min=3, max=255),
        error_messages={
            "required": "O campo chave_nome é obrigatório.",
            "null": "O campo chave_nome não pode ser nulo.",
            "validator_failed": "O campo chave_nome deve ter exatamente 2 caracteres."
        }
    )
