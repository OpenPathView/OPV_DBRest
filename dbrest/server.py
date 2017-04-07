from flask import Flask
import flask_restless
from flask_cors import CORS

from dbrest import models

ALL_METHODS = ['GET', 'POST', 'PATCH', 'DELETE']

app = Flask(__name__)
CORS(app, expose_headers='Link')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True

def makeAndRun(db_location, host, debug=False):
    if db_location and db_location != "in-memory":
        app.config['SQLALCHEMY_DATABASE_URI'] = db_location
    models.db.init_app(app)

    with app.test_request_context():
        models.db.create_all()
        manager = flask_restless.APIManager(app, flask_sqlalchemy_db=models.db)

    manager.create_api(models.Campaign, primary_key="id_campaign", methods=ALL_METHODS, url_prefix='/api/v1')
    manager.create_api(models.Sensors, primary_key="id_sensors", methods=ALL_METHODS, url_prefix='/api/v1')
    manager.create_api(models.Lot, primary_key="id_lot", methods=ALL_METHODS, url_prefix='/api/v1')
    manager.create_api(models.Cp, primary_key="id_cp", methods=ALL_METHODS, url_prefix='/api/v1')
    manager.create_api(models.Panorama, primary_key="id_panorama", methods=ALL_METHODS, url_prefix='/api/v1')
    manager.create_api(models.Tile, primary_key="id_tile", methods=ALL_METHODS, url_prefix='/api/v1')

    app.run(host=host)
