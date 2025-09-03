from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Date
from helpers.database import db
from marshmallow import Schema, fields, validate, ValidationError, validates
from flask_restful import fields as flaskFields

class DateFormat(flaskFields.Raw):
    def format(self, value):
        return value.isoformat() if value else None

responsavel_fields = {
    'responsavel_id': flaskFields.Integer,
    'responsavel_nome': flaskFields.String,
    'responsavel_siap': flaskFields.String,
    'responsavel_cpf': flaskFields.String,
    'responsavel_data_nascimento': DateFormat
}


def validate_positive(value):
    if value < 0:
        raise ValidationError("O valor deve ser um número inteiro não negativo.")
    

class Responsavel(db.Model):
    __tablename__ = "responsavel"

    responsavel_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    responsavel_nome: Mapped[str] = mapped_column(String(255), nullable=False)
    responsavel_siap: Mapped[str] = mapped_column(String(255), nullable=True, unique=True)
    responsavel_cpf: Mapped[str] = mapped_column(String(255), nullable=True, unique=True)
    responsavel_data_nascimento: Mapped[Date] = mapped_column(Date, nullable=True)

    reserva = relationship("Reserva", back_populates="responsavel")

class ResponsavelSchema(Schema):
    responsavel_id = fields.Int(dump_only=True) 

    responsavel_nome = fields.Str(
        required=True,
        validate=validate.Length(min=4, max=255),
        error_messages={"required": "O campo responsavel_nome é obrigatório.", 
            "null": "O campo responsavel_nome não pode ser nulo.", 
            "validator_failed": "O campo responsavel_nome deve ter entre 4 a 255 caracteres."})

    responsavel_siap = fields.Str(
        required=True,  
        validate=validate.Length(min=4, max=255),
        error_messages={"required": "O campo responsavel_siap é obrigatório.", 
            "null": "O campo responsavel_siap não pode ser nulo.", 
            "validator_failed": "O campo responsavel_siap deve ter entre 4 a 255 caracteres."})
    
    responsavel_cpf = fields.Str(
        required=True,                         
        validate=validate.Length(min=4, max=255),
        error_messages={"required": "O campo responsavel_cpf é obrigatório.", 
            "null": "O campo responsavel_cpf não pode ser nulo.", 
            "validator_failed": "O campo responsavel_cpf deve ter entre 4 a 255 caracteres."})
    
    
    responsavel_data_nascimento = fields.Date(
        required=True,
        error_messages={
            "required": "O campo data de nascimento é obrigatório.",
            "invalid": "O campo data de nascimento deve estar no formato YYYY-MM-DD."
        }
    )

    @validates("responsavel_cpf")
    def validate_unique_cpf(self, value, **kwargs):
        if db.session.query(Responsavel).filter_by(responsavel_cpf=value).first():
            raise ValidationError({"unique": "Já existe um Responsavel cadastrado com esse CPF."})

    @validates("responsavel_siap")
    def validate_unique_siap(self, value, **kwargs):
        if db.session.query(Responsavel).filter_by(responsavel_siap=value).first():
            raise ValidationError({"unique": "Já existe um Responsavel cadastrado com esse SIAP."})

