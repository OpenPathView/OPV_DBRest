from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref

from .helper import CompositePrimaryKeyHackedQuery, get_malette_id

db = SQLAlchemy(query_class=CompositePrimaryKeyHackedQuery)

# Declaration of models
#
# /!\ Warning: Order of primary_keys is really important because of the query hack
#              e.g to being able to get campaign with id_campaign = 0; id_malette = 1
#                  you will have to call api/campaign/0-1 because id_campaign is before id_malette

class Campaign(db.Model):
    id_campaign = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_malette = db.Column(db.Integer, primary_key=True, default=get_malette_id())

    name = db.Column(db.String(50))
    decription = db.Column(db.String(150))
    id_rederbro = db.Column(db.Integer)


class Sensors(db.Model):
    id_sensors = db.Column(db.Integer, primary_key=True)
    id_malette = db.Column(db.Integer, primary_key=True, default=get_malette_id())
    # gps
    lng = db.Column(db.Float)
    lat = db.Column(db.Float)
    alt = db.Column(db.Float)
    # Compass
    degrees = db.Column(db.Float)
    minutes = db.Column(db.Float)

class Lot(db.Model):
    id_lot = db.Column(db.Integer, primary_key=True)
    id_malette = db.Column(db.Integer, primary_key=True, default=get_malette_id())

    pictures_path = db.Column(db.String(100), nullable=False)
    goprofailed = db.Column(db.Integer, nullable=False)
    takenDate = db.Column(db.DateTime, nullable=False)

    id_sensors = db.Column(db.Integer, nullable=False)
    id_sensors_malette = db.Column(db.Integer, nullable=False)
    sensors = db.relationship('Sensors', uselist=False, backref=backref('lot', lazy='dynamic'))

    id_campaign = db.Column(db.Integer, nullable=False)
    id_campaign_malette = db.Column(db.Integer, nullable=False)
    campaign = db.relationship('Campaign', backref=backref('lots', lazy='dynamic'))

    id_tile = db.Column(db.Integer, nullable=True)
    id_tile_malette = db.Column(db.Integer, nullable=True)
    tile = db.relationship('Tile', uselist=False, backref=backref('lot', lazy='dynamic'))

    __table_args__ = (db.ForeignKeyConstraint(['id_campaign', 'id_campaign_malette'],
                                              ['campaign.id_campaign', 'campaign.id_malette']),
                      db.ForeignKeyConstraint(['id_sensors', 'id_sensors_malette'],
                                              ['sensors.id_sensors', 'sensors.id_malette']),
                      db.ForeignKeyConstraint(['id_tile', 'id_tile_malette'],
                                              ['tile.id_tile', 'tile.id_malette']))

class Cp(db.Model):
    id_cp = db.Column(db.Integer, primary_key=True)
    id_malette = db.Column(db.Integer, primary_key=True, default=get_malette_id())

    search_algo_version = db.Column(db.String(20), nullable=False)
    nb_cp = db.Column(db.Integer, nullable=True)
    stichable = db.Column(db.Boolean, nullable=True)
    optimized = db.Column(db.Boolean, default=False)
    pto_dir = db.Column(db.String(100), nullable=False)

    id_lot = db.Column(db.Integer, nullable=False)
    id_lot_malette = db.Column(db.Integer, nullable=False)
    lot = db.relationship(Lot, backref=backref('cps', lazy='dynamic'))

    __table_args__ = (db.ForeignKeyConstraint(['id_lot', 'id_lot_malette'], ['lot.id_lot', 'lot.id_malette']),)

class Panorama(db.Model):
    id_panorama = db.Column(db.Integer, primary_key=True)
    id_malette = db.Column(db.Integer, primary_key=True, default=get_malette_id())

    equirectangular_path = db.Column(db.String(100))

    id_cp = db.Column(db.Integer, nullable=False)
    id_cp_malette = db.Column(db.Integer, nullable=False)
    cp = db.relationship(Cp, backref=backref('panorama', lazy='dynamic'))

    __table_args__ = (db.ForeignKeyConstraint(['id_cp', 'id_cp_malette'], ['cp.id_cp', 'cp.id_malette']),)

class Tile(db.Model):
    id_tile = db.Column(db.Integer, primary_key=True)
    id_malette = db.Column(db.Integer, primary_key=True, default=get_malette_id())

    param_location = db.Column(db.String(100), nullable=False)
    fallback_path = db.Column(db.String(100), nullable=False)
    extension = db.Column(db.String(5), nullable=False)
    resolution = db.Column(db.Integer, nullable=False)
    max_level = db.Column(db.Integer, nullable=False)
    cube_resolution = db.Column(db.Integer, nullable=False)

    id_panorama = db.Column(db.Integer, nullable=False)
    id_panorama_malette = db.Column(db.Integer, nullable=False)
    panorama = db.relationship(Panorama, uselist=False, backref=backref('tiles', lazy='dynamic'))

    __table_args__ = (db.ForeignKeyConstraint(['id_panorama', 'id_panorama_malette'], ['panorama.id_panorama', 'panorama.id_malette']),)
