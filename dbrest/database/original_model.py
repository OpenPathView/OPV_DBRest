#!/usr/bin/env python
# coding: utf-8

# Copyright (C) 2017 Open Path View
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

# Contributors: BERNARD Benjamin, GOUGE Tristan
# Email: team@openpathview.fr
# Description:  Original model of the database, considerer it as the model version 0. Used to test migration script.
# DO NOT CHANGE THIS MODEL

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geography
import json

from create_db_original import get_malette_id

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
    active = sa.Column(sa.Boolean, nullable=True)

    id_sensors = sa.Column(sa.Integer, nullable=False)
    id_sensors_malette = sa.Column(sa.Integer, nullable=False)
    sensors = relationship('Sensors', backref=backref('lot', uselist=False))

    id_campaign = sa.Column(sa.Integer, nullable=False)
    id_campaign_malette = sa.Column(sa.Integer, nullable=False)
    campaign = relationship('Campaign', backref=backref('lots'))

    id_tile = sa.Column(sa.Integer, nullable=True)
    id_tile_malette = sa.Column(sa.Integer, nullable=True)
    tile = relationship('Tile')

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
    nearest_cp_found = sa.Column(sa.Boolean, nullable=True)
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

    id_lot_from = sa.Column(sa.Integer, nullable=False)
    id_lot_malette_from = sa.Column(sa.Integer, nullable=False)
    lot_from = relationship(Lot, backref=backref('track_edges'),
                                 foreign_keys=(id_lot_from,
                                               id_lot_malette_from))

    id_lot_to = sa.Column(sa.Integer, nullable=False)
    id_lot_malette_to = sa.Column(sa.Integer, nullable=False)
    lot_to = relationship(Lot, foreign_keys=(id_lot_to, id_lot_malette_to))

    active = sa.Column(sa.Boolean, nullable=True)

    pitch = sa.Column(sa.Float)
    yaw = sa.Column(sa.Float)
    targetPitch = sa.Column(sa.Float)
    targetYaw = sa.Column(sa.Float)

    __table_args__ = (
        sa.ForeignKeyConstraint(
            ['id_lot_from', 'id_lot_malette_from'],
            ['lot.id_lot', 'lot.id_malette']),
        sa.ForeignKeyConstraint(
            ['id_lot_to', 'id_lot_malette_to'],
            ['lot.id_lot', 'lot.id_malette']))

# !!! DO NOT CHANGE THIS MODEL !!!
