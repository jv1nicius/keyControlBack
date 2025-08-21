from helpers.application import app, api
from helpers.database import db
from helpers.CORS import cors
from resources.IndexResource import IndexResource
from resources.SalaResource import SalasResource, SalaResource
from resources.ReservaResource import ReservasResource, ReservaResource
from resources.ResponsavelResource import ResponsaveisResource, ResponsavelResource

cors.init_app(app)

api.add_resource(IndexResource, '/')
api.add_resource(SalasResource, '/salas')
api.add_resource(SalaResource, '/salas/<int:sala_id>')
api.add_resource(ReservasResource, '/reservas')
api.add_resource(ReservaResource, '/reservas/<int:reserva_id>')
api.add_resource(ResponsaveisResource, '/responsaveis')
api.add_resource(ResponsavelResource, '/responsaveis/<int:responsavel_id>')


if __name__ == "__main__":
    app.run(debug=True)
