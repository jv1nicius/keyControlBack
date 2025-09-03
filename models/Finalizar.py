from helpers.database import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, ForeignKey, DateTime
from marshmallow import Schema, fields, validate, ValidationError
from flask_restful import fields as flaskFields


finalizacao_fields = {
    'finalizacao_id': flaskFields.Integer,
    'reserva_id': flaskFields.Integer,
    'data_hora_finalizacao': flaskFields.DateTime
}


def validate_positive(value):
    if value < 0:
        raise ValidationError("O valor deve ser um número inteiro não negativo.")


class Finalizar(db.Model):
    __tablename__ = "finalizacao"

    finalizacao_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reserva_id: Mapped[int] = mapped_column(Integer, ForeignKey('reserva.reserva_id'), nullable=False)
    data_hora_finalizacao: Mapped[DateTime] = mapped_column(DateTime, nullable=False)


class FinalizarSchema(Schema):
    finalizacao_id = fields.Int(dump_only=True)
    reserva_id = fields.Int(
        required=True, 
        validate=validate_positive,
        error_messages={
            "required": "O campo reserva_id é obrigatório.",
            "null": "O campo reserva_id não pode ser nulo.",
            "validator_failed": "O campo reserva_id deve ser valido(Maior que 0)."
        }
    )
    data_hora_finalizacao = fields.DateTime(
        required=True,
        format="iso",
        error_messages={
            "required": "O campo data_hora_finalizacao é obrigatório.",
            "invalid": "Formato inválido, use ISO 8601 (ex: 2025-08-17T14:00:00)."
        }
    )