from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer
from helpers.database import db
from marshmallow import Schema, fields, validate, ValidationError
from flask_restful import fields as flaskFields

responsavel_fields = {
    'responsavel_id': flaskFields.Integer,
    'responsavel_nome': flaskFields.String
}


def validate_positive(value):
    if value < 0:
        raise ValidationError("O valor deve ser um número inteiro não negativo.")
    

class Responsavel(db.Model):
    __tablename__ = "responsavel"

    responsavel_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    responsavel_nome: Mapped[str] = mapped_column(String(255), nullable=False)

    reserva = relationship("Reserva", back_populates="responsavel")

class ResponsavelSchema(Schema):
    responsavel_id = fields.Int(dump_only=True) 
    responsavel_nome = fields.Str(required=True,
    validate=validate.Length(min=4, max=255),
    error_messages={"required": "O campo responsavel_nome é obrigatório.", 
    "null": "O campo responsavel_nome não pode ser nulo.", 
    "validator_failed": "O campo responsavel_nome deve ter entre 4 a 255 caracteres."})
