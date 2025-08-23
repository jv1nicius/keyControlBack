from flask import request, abort
from flask_restful import Resource, marshal
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from helpers.database import db
from helpers.logging import logger, log_exception
from models.Reserva import Reserva, ReservaSchema, reserva_fields
from datetime import datetime
from models.Responsavel import Responsavel
from models.Sala import Sala


class ReservasResource(Resource):
    def get(self):
        logger.info("GET ALL - Listagem de Reservas")

        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 50))

        try:
            query = db.select(Reserva).order_by(Reserva.reserva_id)
            reservas = db.session.execute(
                query.offset((page - 1) * per_page).limit(per_page)
            ).scalars().all()

            logger.info("Reservas retornadas com sucesso")
            return marshal(reservas, reserva_fields), 200

        except SQLAlchemyError:
            log_exception("Erro SQLAlchemy ao buscar reservas")
            db.session.rollback()
            abort(500, description="Erro ao buscar reservas no banco de dados.")

        except Exception:
            log_exception("Erro inesperado ao buscar reservas")
            abort(500, description="Erro interno inesperado.")


    def post(self):
        logger.info("POST - Nova reserva")
        schema = ReservaSchema()
        dados = request.get_json()
        
        sala_id = dados.get("sala_id")
        responsavel_id = dados.get("responsavel_id")
        data_hora_inicio = dados.get("data_hora_inicio")
        data_hora_fim = dados.get("data_hora_fim")

        try:
            
            data_hora_inicio = datetime.fromisoformat(data_hora_inicio)
            data_hora_fim = datetime.fromisoformat(data_hora_fim)
            
            sala = db.session.get(Sala, sala_id)
            if not sala:
                return {"erro": "Sala não encontrada"}, 404
            
            responsavel = db.session.get(Responsavel, responsavel_id)
            if not responsavel:
                return {"erro": "Responsável não encontrado"}, 404
            
            reservas_conflict = db.session.query(Reserva).filter(
                Reserva.sala_id == sala_id,
                Reserva.data_hora_inicio < data_hora_fim,
                Reserva.data_hora_fim > data_hora_inicio
            ).all()
            
            if reservas_conflict:
                return {"erro": "A sala não está disponível para o período solicitado."}, 409
            
            validado = schema.load(dados)
            nova_reserva = Reserva(**validado)
            db.session.add(nova_reserva)
            db.session.commit()
            return marshal(nova_reserva, reserva_fields), 201

        except ValidationError as err:
            return {"erro": "Dados inválidos", "detalhes": err.messages}, 422
        except SQLAlchemyError:
            log_exception("Erro SQLAlchemy ao inserir reserva")
            db.session.rollback()
            abort(500, description="Erro ao inserir reserva no banco.")
        except Exception:
            log_exception("Erro inesperado ao inserir reserva")
            abort(500, description="Erro interno inesperado.")


class ReservaResource(Resource):
    def get(self, reserva_id):
        logger.info(f"GET BY reserva_id - Reserva {reserva_id}")
        try:
            reserva = db.session.get(Reserva, reserva_id)
            if not reserva:
                return {"erro": "Mesorregião não encontrada"}, 404
            return marshal(reserva, reserva_fields), 200

        except SQLAlchemyError:
            log_exception("Erro SQLAlchemy ao buscar Reserva")
            abort(500, description="Erro ao buscar Reserva no banco de dados.")
        except Exception:
            log_exception("Erro inesperado ao buscar Reserva")
            abort(500, description="Erro interno inesperado.")


    def put(self, reserva_id):
        logger.info(f"PUT - Reserva {reserva_id}")
        schema = ReservaSchema()
        dados = request.get_json()

        try:
            reserva = db.session.get(Reserva, reserva_id)
            if not reserva:
                return {"erro": "Reserva não encontrada"}, 404

            atualizados = schema.load(dados, partial=True)
            for campo, valor in atualizados.items():
                setattr(reserva, campo, valor)

            db.session.commit()
            return marshal(reserva, reserva_fields), 200

        except ValidationError as err:
            return {"erro": "Dados inválidos", "detalhes": err.messages}, 422
        except SQLAlchemyError:
            log_exception("Erro SQLAlchemy ao atualizar reserva")
            db.session.rollback()
            abort(500, description="Erro ao atualizar reserva.")
        except Exception:
            log_exception("Erro inesperado ao atualizar reserva")
            abort(500, description="Erro interno inesperado.")

    def delete(self, reserva_id):
        logger.info(f"DELETE - Reserva {reserva_id}")
        try:
            reserva = db.session.get(Reserva, reserva_id)
            if not reserva:
                return {"erro": "Reserva não encontrada"}, 404

            db.session.delete(reserva)
            db.session.commit()
            return {"mensagem": "Reserva removida com sucesso"}, 200


        except SQLAlchemyError:
            log_exception("Erro SQLAlchemy ao remover Reserva")
            db.session.rollback()
            abort(500, description="Erro ao remover Reserva.")
        except Exception:
            log_exception("Erro inesperado ao remover Reserva")
            abort(500, description="Erro interno inesperado.")
