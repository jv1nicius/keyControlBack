from flask import request, abort
from flask_restful import Resource, marshal
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from helpers.database import db
from helpers.logging import logger, log_exception
from datetime import datetime
from models.Finalizar import Finalizar, FinalizarSchema, finalizacao_fields
from models.Reserva import Reserva
from models.Historico import Historico


class FinalizacõesResource(Resource):
    def get(self):
        logger.info("GET ALL - Listagem de Finalizações")

        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 50))

        try:
            query = db.select(Finalizar).order_by(Finalizar.finalizacao_id)
            finalizacoes = db.session.execute(
                query.offset((page - 1) * per_page).limit(per_page)
            ).scalars().all()

            logger.info("Finalizações retornadas com sucesso")
            return marshal(finalizacoes, finalizacao_fields), 200

        except SQLAlchemyError:
            log_exception("Erro SQLAlchemy ao buscar Finalizações")
            db.session.rollback()
            abort(500, description="Erro ao buscar Finalizações no banco de dados.")

        except Exception:
            log_exception("Erro inesperado ao buscar Finalizações")
            abort(500, description="Erro interno inesperado.")


    def post(self):
        logger.info("POST - Nova Finalização")
        schema = FinalizarSchema()
        dados = request.get_json()
        
        reserva_id = dados.get("reserva_id")
        data_hora_finalizacao = dados.get("data_hora_finalizacao")

        try:
            data_hora_finalizacao = datetime.fromisoformat(data_hora_finalizacao)
            reserva = db.session.get(Reserva, reserva_id)
            if not reserva:
                return {"erro": "Reserva não encontrada"}, 404
            
            validado = schema.load(dados)
            nova_finalizacao = Finalizar(**validado)
            db.session.add(nova_finalizacao)

            novo_historico = Historico(
                reserva_id=reserva.reserva_id,
                sala_id=reserva.sala_id,
                responsavel_id=reserva.responsavel_id,
                data_hora_inicio=reserva.data_hora_inicio,
                data_hora_fim=data_hora_finalizacao
            )
            db.session.add(novo_historico)

            db.session.commit()
            logger.info(
                f"Finalização {nova_finalizacao.finalizacao_id} criada "
                f"e reserva {reserva.reserva_id} adicionada ao histórico!"
            )

            return marshal(nova_finalizacao, finalizacao_fields), 201

        except ValidationError as err:
            return {"erro": "Dados inválidos", "detalhes": err.messages}, 422
        except SQLAlchemyError:
            log_exception("Erro SQLAlchemy ao inserir finalização/histórico")
            db.session.rollback()
            abort(500, description="Erro ao inserir finalização/histórico no banco.")
        except Exception:
            log_exception("Erro inesperado ao inserir finalização/histórico")
            abort(500, description="Erro interno inesperado.")



class FinalizarResource(Resource):
    def get(self, finalizar_id):
        logger.info(f"GET BY finalizacao_id - Finalização {finalizar_id}")
        try:
            finalizar = db.session.get(Finalizar, finalizar_id)
            if not finalizar:
                return {"erro": "Finalização não encontrada"}, 404
            return marshal(finalizar, finalizacao_fields), 200

        except SQLAlchemyError:
            log_exception("Erro SQLAlchemy ao buscar Finalização")
            abort(500, description="Erro ao buscar Finalização no banco de dados.")
        except Exception:
            log_exception("Erro inesperado ao buscar Finalização")
            abort(500, description="Erro interno inesperado.")


    def put(self, finalizar_id):
        logger.info(f"PUT - Finalização {finalizar_id}")
        schema = FinalizarSchema()
        dados = request.get_json()

        try:
            finalizacao = db.session.get(Finalizar, finalizacao_fields)
            if not finalizacao:
                return {"erro": "Finalização não encontrada"}, 404

            atualizados = schema.load(dados, partial=True)
            for campo, valor in atualizados.items():
                setattr(finalizacao, campo, valor)

            db.session.commit()
            return marshal(finalizacao, finalizacao_fields), 200

        except ValidationError as err:
            return {"erro": "Dados inválidos", "detalhes": err.messages}, 422
        except SQLAlchemyError:
            log_exception("Erro SQLAlchemy ao atualizar Finalização")
            db.session.rollback()
            abort(500, description="Erro ao atualizar Finalização.")
        except Exception:
            log_exception("Erro inesperado ao atualizar Finalização")
            abort(500, description="Erro interno inesperado.")

    def delete(self, finalizar_id):
        logger.info(f"DELETE - Finalização {finalizar_id}")
        try:
            finalizacao = db.session.get(Finalizar, finalizar_id)
            if not finalizacao:
                return {"erro": "finalizacao não encontrada"}, 404

            db.session.delete(finalizacao)
            db.session.commit()
            return {"mensagem": "finalizacao removida com sucesso"}, 200


        except SQLAlchemyError:
            log_exception("Erro SQLAlchemy ao remover finalizacao")
            db.session.rollback()
            abort(500, description="Erro ao remover finalizacao.")
        except Exception:
            log_exception("Erro inesperado ao remover finalizacao")
            abort(500, description="Erro interno inesperado.")
