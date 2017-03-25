from flask import Flask
import flask_restless
from flask_cors import CORS

from . import db

app = Flask(__name__)
CORS(app, expose_headers='Link')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True


#    manager.create_api(db.Lot, methods=['GET', 'POST', 'DELETE', 'PATCH'])
#    manager.create_api(db.Sensors, methods=['GET', 'POST', 'DELETE', 'PATCH'])
#    manager.create_api(db.Cp, methods=['GET', 'POST', 'DELETE', 'PATCH'])
#    manager.create_api(db.Panorama, methods=['GET', 'POST', 'DELETE', 'PATCH'])
#    manager.create_api(db.Tile, methods=['GET', 'POST', 'DELETE', 'PATCH'])

def makeAndRun(db_location, host, debug=False):

    if db_location and db_location != "in-memory":
        app.config['SQLALCHEMY_DATABASE_URI'] = db_location
    db.db.init_app(app)

    with app.test_request_context():
        db.db.create_all()

    manager = flask_restless.APIManager(app)
    manager.create_api(db.Campaign)

    app.run(host=host)
