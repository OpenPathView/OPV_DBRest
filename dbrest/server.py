from flask import Flask, request
from flask_potion.routes import Relation
from flask_potion import Api, fields, ModelResource

from .db import *

dbg = False

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

class SensorsRessource(ModelResource):
    lot = Relation('lot')

    class Meta:
        model = Sensors

class CampaignRessource(ModelResource):
    lots = Relation('lot')

    class Meta:
        model = Campaign

class LotRessource(ModelResource):
    cps = Relation('cp')

    class Meta:
        model = Lot

    class Schema:
        campaign = fields.ToOne('campaign')
        sensors = fields.ToOne('sensors')

class ParonamaRessource(ModelResource):
    tiles = Relation('tile')

    class Meta:
        model = Panorama

    class Schema:
        cp = fields.ToOne('cp')

class CpRessource(ModelResource):
    panorama = Relation('panorama')

    class Meta:
        model = Cp

    class Schema:
        lot = fields.ToOne('lot')

class TileRessource(ModelResource):
    class Meta:
        model = Tile

    class Schema:
        panorama = fields.ToOne('panorama')


api = Api(app)
api.add_resource(TileRessource)
api.add_resource(ParonamaRessource)
api.add_resource(CpRessource)
api.add_resource(LotRessource)
api.add_resource(SensorsRessource)
api.add_resource(CampaignRessource)

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/shutdown', methods=['POST'])
def shutdown():
    if dbg:
        shutdown_server()
        return 'Server shutting down...'
    return "You can't shut the server down"

def makeAndRun(db_location, debug=False):
    global dbg
    dbg = debug
    if db_location and db_location != "in-memory":
        app.config['SQLALCHEMY_DATABASE_URI'] = db_location
    db.init_app(app)
    with app.test_request_context():
        db.create_all()
    app.run()
