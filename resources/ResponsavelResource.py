from flask import request, abort
from flask_restful import Resource, marshal
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from helpers.database import db
from helpers.logging import logger, log_exception
from models.Responsavel import Responsavel, ResponsavelSchema, responsavel_fields


class ResponsaveisResource(Resource):
    def get(self):
        logger.info("GET ALL - Listagem de Responsaveis")

        try:
            query = db.select(Responsavel).order_by(Responsavel.responsavel_id)
            responsaveis = db.session.execute(query).scalars().all()

            logger.info("Responsaveis retornadas com sucesso")
            return marshal(responsaveis, responsavel_fields), 200

        except SQLAlchemyError:
            log_exception("Erro SQLAlchemy ao buscar Responsaveis")
            db.session.rollback()
            abort(500, description="Erro ao buscar Responsaveis no banco de dados.")

        except Exception:
            log_exception("Erro inesperado ao buscar Responsaveis")
            abort(500, description="Erro interno inesperado.")


    def post(self):
        logger.info("POST - Novo Responsavel")
        schema = ResponsavelSchema()
        dados = request.get_json()

        try:
            validado = schema.load(dados)
            novo_responsavel = Responsavel(**validado)
            db.session.add(novo_responsavel)
            db.session.commit()
            return marshal(novo_responsavel, responsavel_fields), 201

        except ValidationError as err:
            return {"erro": "Dados inválidos", "detalhes": err.messages}, 422
        except SQLAlchemyError:
            log_exception("Erro SQLAlchemy ao inserir Responsavel")
            db.session.rollback()
            abort(500, description="Erro ao inserir Responsavel no banco.")
        except Exception:
            log_exception("Erro inesperado ao inserir Responsavel")
            abort(500, description="Erro interno inesperado.")


class ResponsavelResource(Resource):
    def get(self, responsavel_id):
        logger.info(f"GET BY responsavel_id - Responsavel {responsavel_id}")
        try:
            responsavel = db.session.get(Responsavel, responsavel_id)
            if not responsavel:
                return {"erro": "Responsavel não encontrado"}, 404
            return marshal(responsavel, responsavel_fields), 200

        except SQLAlchemyError:
            log_exception("Erro SQLAlchemy ao buscar responsavel")
            abort(500, description="Erro ao buscar responsavel no banco de dados.")
        except Exception:
            log_exception("Erro inesperado ao buscar responsavel")
            abort(500, description="Erro interno inesperado.")

    def put(self, responsavel_id):
        logger.info(f"PUT - Responsavel {responsavel_id}")
        schema = ResponsavelSchema()
        dados = request.get_json()

        try:
            responsavel = db.session.get(Responsavel, responsavel_id)
            if not responsavel:
                return {"erro": "Responsavel não encontrada"}, 404

            atualizados = schema.load(dados, partial=True)
            for campo, valor in atualizados.items():
                setattr(responsavel, campo, valor)

            db.session.commit()
            return marshal(responsavel, responsavel_fields), 200

        except ValidationError as err:
            return {"erro": "Dados inválidos", "detalhes": err.messages}, 422
        except SQLAlchemyError:
            log_exception("Erro SQLAlchemy ao atualizar responsavel")
            db.session.rollback()
            abort(500, description="Erro ao atualizar responsavel.")
        except Exception:
            log_exception("Erro inesperado ao atualizar responsavel")
            abort(500, description="Erro interno inesperado.")

    def delete(self, responsavel_id):
        logger.info(f"DELETE - responsavel {responsavel_id}")
        try:
            responsavel = db.session.get(Responsavel, responsavel_id)
            if not responsavel:
                return {"erro": "responsavel não encontrada"}, 404

            db.session.delete(responsavel)
            db.session.commit()
            return {"mensagem": "responsavel removida com sucesso"}, 200

        except SQLAlchemyError:
            log_exception("Erro SQLAlchemy ao remover responsavel")
            db.session.rollback()
            abort(500, description="Erro ao remover responsavel.")
        except Exception:
            log_exception("Erro inesperado ao remover responsavel")
            abort(500, description="Erro interno inesperado.")
