from flask import request, abort
from flask_restful import Resource, marshal
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from helpers.database import db
from helpers.logging import logger, log_exception
from models.Historico import Historico, HistoricoSchema, historico_fields
from datetime import datetime


class HistoricosResource(Resource):
    def get(self):
        logger.info("GET ALL - Listagem de Historicos")

        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 50))

        try:
            query = db.select(Historico).order_by(Historico.historico_id)
            historicos = db.session.execute(
                query.offset((page - 1) * per_page).limit(per_page)
            ).scalars().all()

            logger.info("Historicos retornadas com sucesso")
            return marshal(historicos, historico_fields), 200

        except SQLAlchemyError:
            log_exception("Erro SQLAlchemy ao buscar Historicos")
            db.session.rollback()
            abort(500, description="Erro ao buscar Historicos no banco de dados.")

        except Exception:
            log_exception("Erro inesperado ao buscar Historicos")
            abort(500, description="Erro interno inesperado.")


    def post(self):
        logger.info("POST - Nova Historico")
        schema = HistoricoSchema()
        dados = request.get_json()

        try:
            validado = schema.load(dados)
            novo_historico = Historico(**validado)
            db.session.add(novo_historico)
            db.session.commit()
            logger.info(f"Historico {novo_historico.historico_id} criada com sucesso!")
            return marshal(novo_historico, historico_fields), 201

        except ValidationError as err:
            return {"erro": "Dados inválidos", "detalhes": err.messages}, 422
        except SQLAlchemyError:
            log_exception("Erro SQLAlchemy ao inserir Historico")
            db.session.rollback()
            abort(500, description="Erro ao inserir Historico no banco.")
        except Exception:
            log_exception("Erro inesperado ao inserir Historico")
            abort(500, description="Erro interno inesperado.")


class HistoricoResource(Resource):
    def get(self, historico_id):
        logger.info(f"GET BY historico_id - historico {historico_id}")
        try:
            historico = db.session.get(Historico, historico_id)
            if not historico:
                return {"erro": "historico não encontrada"}, 404
            return marshal(historico, historico_fields), 200

        except SQLAlchemyError:
            log_exception("Erro SQLAlchemy ao buscar historico")
            abort(500, description="Erro ao buscar historico no banco de dados.")
        except Exception:
            log_exception("Erro inesperado ao buscar historico")
            abort(500, description="Erro interno inesperado.")


    def put(self, historico_id):
        logger.info(f"PUT - historico {historico_id}")
        schema = HistoricoSchema()
        dados = request.get_json()

        try:
            historico = db.session.get(Historico, historico_id)
            if not historico:
                return {"erro": "Historico não encontrada"}, 404

            atualizados = schema.load(dados, partial=True)
            for campo, valor in atualizados.items():
                setattr(historico, campo, valor)

            db.session.commit()
            return marshal(historico, historico_fields), 200

        except ValidationError as err:
            return {"erro": "Dados inválidos", "detalhes": err.messages}, 422
        except SQLAlchemyError:
            log_exception("Erro SQLAlchemy ao atualizar Historico")
            db.session.rollback()
            abort(500, description="Erro ao atualizar Historico.")
        except Exception:
            log_exception("Erro inesperado ao atualizar Historico")
            abort(500, description="Erro interno inesperado.")

    def delete(self, historico_id):
        logger.info(f"DELETE - Historico {historico_id}")
        try:
            historico = db.session.get(Historico, historico_id)
            if not historico:
                return {"erro": "Historico não encontrada"}, 404

            db.session.delete(historico)
            db.session.commit()
            return {"mensagem": "Historico removida com sucesso"}, 200


        except SQLAlchemyError:
            log_exception("Erro SQLAlchemy ao remover Historico")
            db.session.rollback()
            abort(500, description="Erro ao remover Historico.")
        except Exception:
            log_exception("Erro inesperado ao remover Historico")
            abort(500, description="Erro interno inesperado.")
