from flask import request, abort
from flask_restful import Resource, marshal
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from helpers.database import db
from helpers.logging import logger, log_exception
from models.Sala import Sala, SalaSchema, sala_fields


class SalasResource(Resource):
    def get(self):
        logger.info("GET ALL - Listagem de Salas")

        try:
            query = db.select(Sala).order_by(Sala.sala_id)
            salas = db.session.execute(query).scalars().all()

            logger.info("Salas retornadas com sucesso")
            return marshal(salas, sala_fields), 200

        except SQLAlchemyError:
            log_exception("Erro SQLAlchemy ao buscar Salas")
            db.session.rollback()
            abort(500, description="Erro ao buscar Salas no banco de dados.")

        except Exception:
            log_exception("Erro inesperado ao buscar Salas")
            abort(500, description="Erro interno inesperado.")


    def post(self):
        logger.info("POST - Nova Sala")

        schema = SalaSchema()
        dados = request.get_json()

        try:
            validado = schema.load(dados)
            nova_sala = Sala(**validado)
            db.session.add(nova_sala)
            db.session.commit()

            logger.info(f"Sala {nova_sala.sala_id} criada com sucesso!")
            return marshal(nova_sala, sala_fields), 201

        except ValidationError as err:
            logger.warning(f"Erro de validação: {err.messages}")
            return {"erro": "Dados inválidos.", "detalhes": err.messages}, 422

        except SQLAlchemyError:
            log_exception("Erro SQLAlchemy ao inserir Sala")
            db.session.rollback()
            abort(500, description="Erro ao inserir Sala no banco.")

        except Exception:
            log_exception("Erro inesperado no POST Sala")
            abort(500, description="Erro interno inesperado.")


class SalaResource(Resource):
    def get(self, sala_id):
        logger.info(f"GET BY sala_id - Sala ({sala_id})")

        try:
            sala = db.session.get(Sala, sala_id)
            if not sala:
                return {"erro": "Sala não encontrada."}, 404

            return marshal(sala, sala_fields), 200

        except SQLAlchemyError:
            log_exception("Erro SQLAlchemy ao buscar Sala")
            db.session.rollback()
            abort(500, description="Erro ao buscar Sala no banco de dados.")

        except Exception:
            log_exception("Erro inesperado ao buscar Sala")
            abort(500, description="Erro interno inesperado.")


    def put(self, sala_id):
        logger.info(f"PUT - sala_id ({sala_id})")

        schema = SalaSchema()
        dados = request.get_json()

        try:
            sala = db.session.get(Sala, sala_id)
            if not sala:
                return {"erro": "Sala não encontrada."}, 404

            atualizados = schema.load(dados, partial=True)
            for campo, valor in atualizados.items():
                setattr(sala, campo, valor)

            db.session.commit()
            logger.info(f"Sala ({sala_id}) atualizada com sucesso")
            return marshal(sala, sala_fields), 200

        except ValidationError as err:
            logger.warning(f"Erro de validação: {err.messages}")
            return {"erro": "Dados inválidos.", "detalhes": err.messages}, 422

        except SQLAlchemyError:
            log_exception("Erro SQLAlchemy ao atualizar Sala")
            db.session.rollback()
            abort(500, description="Erro ao atualizar Sala no banco.")

        except Exception:
            log_exception("Erro inesperado ao atualizar Sala")
            abort(500, description="Erro interno inesperado.")


    def delete(self, sala_id):
        logger.info(f"DELETE - Sala ({sala_id})")

        try:
            sala = db.session.get(Sala, sala_id)
            if not sala:
                return {"erro": "Sala não encontrada."}, 404

            db.session.delete(sala)
            db.session.commit()

            logger.info(f"Sala ({sala_id}) removida com sucesso")
            return {"mensagem": "Sala removida com sucesso."}, 200

        except SQLAlchemyError:
            log_exception("Erro SQLAlchemy ao remover Sala")
            db.session.rollback()
            abort(500, description="Erro ao remover Sala no banco.")

        except Exception:
            log_exception("Erro inesperado ao remover Sala")
            abort(500, description="Erro interno inesperado.")
