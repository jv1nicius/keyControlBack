from helpers.database import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, ForeignKey, DateTime
from marshmallow import Schema, fields, validate, ValidationError
from flask_restful import fields as flaskFields


reserva_fields = {
    'reserva_id': flaskFields.Integer,
    'sala_id': flaskFields.Integer,
    'responsavel_id': flaskFields.Integer,
    'data_hora_inicio': flaskFields.DateTime,
    'data_hora_fim': flaskFields.DateTime
}


def validate_positive(value):
    if value < 0:
        raise ValidationError("O valor deve ser um número inteiro não negativo.")


class Reserva(db.Model):
    __tablename__ = "reserva"

    reserva_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sala_id: Mapped[int] = mapped_column(Integer, ForeignKey('sala.sala_id'), nullable=False)
    responsavel_id: Mapped[int] = mapped_column(Integer, ForeignKey('responsavel.responsavel_id'), nullable=False)
    data_hora_inicio: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    data_hora_fim: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    sala = relationship("Sala", back_populates="reserva")
    responsavel = relationship("Responsavel", back_populates="reserva")


class ReservaSchema(Schema):
    reserva_id = fields.Int(dump_only=True)
    sala_id = fields.Int(
        required=True, 
        validate=validate_positive,
        error_messages={
            "required": "O campo sala_id é obrigatório.",
            "null": "O campo sala_id não pode ser nulo.",
            "validator_failed": "O campo sala_id deve ser valido(Maior que 0)."
        }
    )
    responsavel_id = fields.Int(
        required=True, 
        validate=validate_positive,
        error_messages={
            "required": "O campo responsavel_id é obrigatório.",
            "null": "O campo responsavel_id não pode ser nulo.",
            "validator_failed": "O campo COresponsavel_id_UF deve ser valido(Maior que 0)"
        }
    )
    data_hora_inicio = fields.DateTime(
        required=True,
        format="iso",
        error_messages={
            "required": "O campo data_hora_inicio é obrigatório.",
            "invalid": "Formato inválido, use ISO 8601 (ex: 2025-08-17T14:00:00)."
        }
    )

    data_hora_fim = fields.DateTime(
        required=True,
        format="iso",
        error_messages={
            "required": "O campo data_hora_fim é obrigatório.",
            "invalid": "Formato inválido, use ISO 8601 (ex: 2025-08-17T16:00:00)."
        }
    )
