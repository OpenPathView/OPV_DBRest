from flask_sqlalchemy import SQLAlchemy, BaseQuery
from sqlalchemy.orm import backref


class HackedQuery(BaseQuery):
    def filter(self, *criterion):
        ncriterion = []
        for crit in criterion:
            ncrits = []

            col = crit.left
            val = crit.right.effective_value

            primary_key_cols = col.table.primary_key
            if col.primary_key and len(primary_key_cols) >= 2:
                vals = val.split("-")

                if len(vals) != len(primary_key_cols):
                    return super().filter(col == 1, col == 0)  # Should be a 404

                for v, primary_key_col in zip(vals, primary_key_cols):
                    ncrits.append(primary_key_col == v)

            if ncrits:
                ncriterion += ncrits
            else:
                ncriterion.append(crit)

        return super().filter(*ncriterion)


db = SQLAlchemy(query_class=HackedQuery)

class Campaign(db.Model):
    id_campaign = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), primary_key=True)
    decription = db.Column(db.String(150))
    id_rederbro = db.Column(db.Integer)

    db.UniqueConstraint(id_campaign, name)

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

    id_tile = db.Column(db.Integer, db.ForeignKey('tile.id_tile'), nullable=True)
    tile = db.relationship('Tile', uselist=False, backref=backref('lot', lazy='dynamic'), foreign_keys=[id_tile])

class Cp(db.Model):
    id_cp = db.Column(db.Integer, primary_key=True)
    search_algo_version = db.Column(db.String(20), nullable=False)
    nb_cp = db.Column(db.Integer, nullable=True)
    stichable = db.Column(db.Boolean, nullable=True)
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
