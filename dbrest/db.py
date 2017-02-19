from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref

db = SQLAlchemy()

class Campaign(db.Model):
    id_campaign = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    decription = db.Column(db.String(150))
    id_rederbro = db.Column(db.Integer)

class Sensors(db.Model):
    id_sensors = db.Column(db.Integer, primary_key=True)
    # gps
    lng = db.Column(db.Float)
    lat = db.Column(db.Float)
    alt = db.Column(db.Float)
    # Compass
    degrees = db.Column(db.Float)
    minutes = db.Column(db.Float)

class Lot(db.Model):
    id_lot = db.Column(db.Integer, primary_key=True)
    pictures_path = db.Column(db.String(100), nullable=False)
    goprofailed = db.Column(db.Integer, nullable=False)
    takenDate = db.Column(db.DateTime, nullable=False)

    id_sensors = db.Column(db.Integer, db.ForeignKey('sensors.id_sensors'), nullable=False)
    sensors = db.relationship('Sensors', uselist=False, backref=backref('lot', lazy='dynamic'), foreign_keys=[id_sensors])

    id_campaign = db.Column(db.Integer, db.ForeignKey('campaign.id_campaign'), nullable=False)
    campaign = db.relationship('Campaign', backref=backref('lots', lazy='dynamic'), foreign_keys=[id_campaign])

    id_tile = db.Column(db.Integer, db.ForeignKey('tile.id_tile'))
    tile = db.relationship('Tile', uselist=False, foreign_keys=[id_tile])

class Cp(db.Model):
    id_cp = db.Column(db.Integer, primary_key=True)
    search_algo_version = db.Column(db.String(20), nullable=False)
    nb_cp = db.Column(db.Integer, nullable=False)
    stichable = db.Column(db.Boolean, nullable=False)
    optimized = db.Column(db.Boolean, default=False)
    pto_dir = db.Column(db.String(100), nullable=False)

    id_lot = db.Column(db.Integer, db.ForeignKey('lot.id_lot'), nullable=False)
    lot = db.relationship(Lot, backref=backref('cps', lazy='dynamic'))

class Panorama(db.Model):
    id_panorama = db.Column(db.Integer, primary_key=True)
    equirectangular_path = db.Column(db.String(100))

    id_cp = db.Column(db.Integer, db.ForeignKey('cp.id_cp'), nullable=False)
    cp = db.relationship(Cp, backref=backref('panorama', lazy='dynamic'))

class Tile(db.Model):
    id_tile = db.Column(db.Integer, primary_key=True)
    param_location = db.Column(db.String(100), nullable=False)
    fallback_path = db.Column(db.String(100), nullable=False)
    extension = db.Column(db.String(5), nullable=False)
    resolution = db.Column(db.Integer, nullable=False)
    max_level = db.Column(db.Integer, nullable=False)
    cube_resolution = db.Column(db.Integer, nullable=False)

    id_panorama = db.Column(db.Integer, db.ForeignKey('panorama.id_panorama'), nullable=False)
    panorama = db.relationship(Panorama, uselist=False, backref=backref('tiles', lazy='dynamic'), foreign_keys=[id_panorama])
