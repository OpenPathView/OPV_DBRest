import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from geoalchemy2 import Geography
import json

from dbrest import settings
from dbrest.helpers import get_malette_id

engine = sa.create_engine(settings.engine_path)
session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()

class GeoJSONGeography(Geography):
    """Allow to get and to return a GeoJSON object instead of WKB"""
    as_binary = 'ST_AsGeoJSON'
    from_text = 'ST_GeomFromGeoJSON'

    def result_processor(self, dialect, coltype):
        def process(value):
            try:
                return json.loads(value)
            except:
                return
        return process

class Campaign(Base):
    __tablename__ = "campaign"

    id_campaign = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    id_malette = sa.Column(sa.Integer, primary_key=True, default=get_malette_id())

    name = sa.Column(sa.String(50))
    decription = sa.Column(sa.String(150))
    id_rederbro = sa.Column(sa.Integer)

class Sensors(Base):
    __tablename__ = "sensors"

    id_sensors = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    id_malette = sa.Column(sa.Integer, primary_key=True, default=get_malette_id())
    # gps
    # SRID 4326 -> WGS 84 (cf. https://en.wikipedia.org/wiki/World_Geodetic_System)
    gps_pos = sa.Column(GeoJSONGeography('POINTZ', srid=4326))
    # Compass
    degrees = sa.Column(sa.Float)
    minutes = sa.Column(sa.Float)

class Lot(Base):
    __tablename__ = "lot"

    id_lot = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    id_malette = sa.Column(sa.Integer, primary_key=True, default=get_malette_id())

    pictures_path = sa.Column(sa.String(100), nullable=False)
    goprofailed = sa.Column(sa.Integer, nullable=False)
    takenDate = sa.Column(sa.DateTime, nullable=False)

    id_sensors = sa.Column(sa.Integer, nullable=False)
    id_sensors_malette = sa.Column(sa.Integer, nullable=False)
    sensors = relationship('Sensors', backref=backref('lot'))

    id_campaign = sa.Column(sa.Integer, nullable=False)
    id_campaign_malette = sa.Column(sa.Integer, nullable=False)
    campaign = relationship('Campaign', backref=backref('lots'))

    id_tile = sa.Column(sa.Integer, nullable=True)
    id_tile_malette = sa.Column(sa.Integer, nullable=True)

    __table_args__ = (
        sa.ForeignKeyConstraint(
            ['id_campaign', 'id_campaign_malette'],
            ['campaign.id_campaign', 'campaign.id_malette']),
        sa.ForeignKeyConstraint(
            ['id_sensors', 'id_sensors_malette'],
            ['sensors.id_sensors', 'sensors.id_malette']),
        sa.ForeignKeyConstraint(
            ['id_tile', 'id_tile_malette'],
            ['tile.id_tile', 'tile.id_malette'])
    )

class Cp(Base):
    __tablename__ = "cp"

    id_cp = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    id_malette = sa.Column(sa.Integer, primary_key=True, default=get_malette_id())

    search_algo_version = sa.Column(sa.String(20), nullable=False)
    nb_cp = sa.Column(sa.Integer, nullable=True)
    stichable = sa.Column(sa.Boolean, nullable=True)
    optimized = sa.Column(sa.Boolean, default=False)
    pto_dir = sa.Column(sa.String(100), nullable=False)

    id_lot = sa.Column(sa.Integer, nullable=False)
    id_lot_malette = sa.Column(sa.Integer, nullable=False)
    lot = relationship(Lot, backref=backref('cps'))

    __table_args__ = (
        sa.ForeignKeyConstraint(
            ['id_lot', 'id_lot_malette'],
            ['lot.id_lot', 'lot.id_malette']),
    )

class Panorama(Base):
    __tablename__ = "panorama"

    id_panorama = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    id_malette = sa.Column(sa.Integer, primary_key=True, default=get_malette_id())

    equirectangular_path = sa.Column(sa.String(100))
    is_photosphere = sa.Column(sa.Boolean, nullable=True, default=False)

    id_cp = sa.Column(sa.Integer, nullable=False)
    id_cp_malette = sa.Column(sa.Integer, nullable=False)
    cp = relationship(Cp, backref=backref('panorama'))

    __table_args__ = (
        sa.ForeignKeyConstraint(
            ['id_cp', 'id_cp_malette'],
            ['cp.id_cp', 'cp.id_malette']),
    )

class Tile(Base):
    __tablename__ = "tile"

    id_tile = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    id_malette = sa.Column(sa.Integer, primary_key=True, default=get_malette_id())

    param_location = sa.Column(sa.String(100), nullable=False)
    fallback_path = sa.Column(sa.String(100), nullable=False)
    extension = sa.Column(sa.String(5), nullable=False)
    resolution = sa.Column(sa.Integer, nullable=False)
    max_level = sa.Column(sa.Integer, nullable=False)
    cube_resolution = sa.Column(sa.Integer, nullable=False)

    id_panorama = sa.Column(sa.Integer, nullable=False)
    id_panorama_malette = sa.Column(sa.Integer, nullable=False)
    panorama = relationship(Panorama, backref=backref('tiles'))

    __table_args__ = (
        sa.ForeignKeyConstraint(
            ['id_panorama', 'id_panorama_malette'],
            ['panorama.id_panorama', 'panorama.id_malette']),
    )

class TrackEdge(Base):
    """A track edge is an edge for a track to an other track, with orientation"""
    __tablename__ = "trackedge"

    id_track_edge = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    id_malette = sa.Column(sa.Integer, primary_key=True, default=get_malette_id())

    id_panorama_from = sa.Column(sa.Integer, nullable=False)
    id_panorama_malette_from = sa.Column(sa.Integer, nullable=False)
    panorama_from = relationship(Panorama, backref=backref('track_edges'),
                                 foreign_keys=(id_panorama_from,
                                               id_panorama_malette_from))

    id_panorama_to = sa.Column(sa.Integer, nullable=False)
    id_panorama_malette_to = sa.Column(sa.Integer, nullable=False)
    panorama_to = relationship(Panorama,
                                 foreign_keys=(id_panorama_to,
                                               id_panorama_malette_to))

    rotx = sa.Column(sa.Float)
    roty = sa.Column(sa.Float)
    rotz = sa.Column(sa.Float)

    __table_args__ = (
        sa.ForeignKeyConstraint(
            ['id_panorama_from', 'id_panorama_malette_from'],
            ['panorama.id_panorama', 'panorama.id_malette']),
        sa.ForeignKeyConstraint(
            ['id_panorama_to', 'id_panorama_malette_to'],
            ['panorama.id_panorama', 'panorama.id_malette']),
    )

def create_all():
    Base.metadata.create_all(engine)
