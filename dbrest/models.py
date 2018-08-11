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
# Description: Database SQLAlchemy model.
# !!! Please refer to README.md if you change this model to commit it (database is versionned) !!!

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geography
import json

from dbrest.helpers import get_malette_id
from dbrest.commons import view

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


class Reconstruction(Base):
    """ An openSFM reconstruction """
    __tablename__ = "reconstruction"

    id_reconstruction = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    id_malette = sa.Column(sa.Integer, primary_key=True, default=get_malette_id())

    # Reference lat Lon alt
    id_ref_lla = sa.Column(sa.Integer, nullable=False)
    id_ref_lla_malette = sa.Column(sa.Integer, nullable=False)
    ref_lla = relationship(Sensors, foreign_keys=(id_ref_lla, id_ref_lla_malette))

    raw_output_files = sa.Column(sa.String(100), nullable=False)
    reconstruction_algo = sa.Column(sa.String(20), nullable=False)

    id_campaign = sa.Column(sa.Integer, nullable=False)
    id_campaign_malette = sa.Column(sa.Integer, nullable=False)
    campaign = relationship(Campaign, foreign_keys=(id_campaign, id_campaign_malette))

    __table_args__ = (
        sa.ForeignKeyConstraint(
            ['id_ref_lla', 'id_ref_lla_malette'],
            ['sensors.id_sensors', 'sensors.id_malette']),
        sa.ForeignKeyConstraint(
            ['id_campaign', 'id_campaign_malette'],
            ['campaign.id_campaign', 'campaign.id_malette']))


class Shot(Base):
    """ Reconstruction shot """
    __tablename__ = "shot"
    id_shot = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    id_malette = sa.Column(sa.Integer, primary_key=True, default=get_malette_id())

    orientation = sa.Column(sa.Integer)
    camera = sa.Column(sa.String(250))
    gps_pos = sa.Column(sa.types.ARRAY(sa.Float, dimensions=3), nullable=False)
    gps_dop = sa.Column(sa.Float)
    rotation = sa.Column(sa.types.ARRAY(sa.Float, dimensions=3), nullable=False)
    translation = sa.Column(sa.types.ARRAY(sa.Float, dimensions=3), nullable=False)
    capture_time = sa.Column(sa.Float)

    id_reconstruction = sa.Column(sa.Integer, nullable=False)
    id_reconstruction_malette = sa.Column(sa.Integer, nullable=False)
    reconstruction = relationship(Reconstruction, foreign_keys=(id_reconstruction, id_reconstruction_malette))

    id_panorama = sa.Column(sa.Integer, nullable=False)
    id_panorama_malette = sa.Column(sa.Integer, nullable=False)
    panorama = relationship(Panorama, foreign_keys=(id_panorama, id_panorama_malette))

    id_corrected_sensors = sa.Column(sa.Integer)
    id_corrected_sensors_malette = sa.Column(sa.Integer)
    corrected_sensor = relationship(Sensors, foreign_keys=(id_corrected_sensors, id_corrected_sensors_malette))

    __table_args__ = (
        sa.ForeignKeyConstraint(
            ['id_reconstruction', 'id_reconstruction_malette'],
            ['reconstruction.id_reconstruction', 'reconstruction.id_malette']),
        sa.ForeignKeyConstraint(
            ['id_panorama', 'id_panorama_malette'],
            ['panorama.id_panorama', 'panorama.id_malette']),
        sa.ForeignKeyConstraint(
            ['id_corrected_sensors', 'id_corrected_sensors_malette'],
            ['sensors.id_sensors', 'sensors.id_malette']))


class Path(Base):
    """ Path between 2 shots """
    __tablename__ = "path"
    id_path = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    id_malette = sa.Column(sa.Integer, primary_key=True, default=get_malette_id())

    id_shot_from = sa.Column(sa.Integer, nullable=False)
    id_shot_malette_from = sa.Column(sa.Integer, nullable=False)
    shot_from = relationship(Shot, foreign_keys=(id_shot_from, id_shot_malette_from))

    id_shot_to = sa.Column(sa.Integer, nullable=False)
    id_shot_malette_to = sa.Column(sa.Integer, nullable=False)
    shot_to = relationship(Shot, foreign_keys=(id_shot_to, id_shot_malette_to))

    active = sa.Column(sa.Boolean, default=True)
    pitch = sa.Column(sa.Float)
    yaw = sa.Column(sa.Float)
    target_pitch = sa.Column(sa.Float)
    target_yaw = sa.Column(sa.Float)
    manual = sa.Column(sa.Boolean, default=False)

    __table_args__ = (
        sa.ForeignKeyConstraint(
            ['id_shot_from', 'id_shot_malette_from'],
            ['shot.id_shot', 'shot.id_malette']),
        sa.ForeignKeyConstraint(
            ['id_shot_to', 'id_shot_malette_to'],
            ['shot.id_shot', 'shot.id_malette']))


# ---- Virtual tour roads/paths ----

class PathNode(Base):
    """ Describe a path node, panorama """
    __tablename__ = "path_node"
    id_path_node = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    id_malette = sa.Column(sa.Integer, primary_key=True, default=get_malette_id())

    id_panorama = sa.Column(sa.Integer, nullable=False)
    id_panorama_malette = sa.Column(sa.Integer, nullable=False)
    panorama = relationship(Panorama, foreign_keys=(id_panorama, id_panorama_malette))

    id_path_details = sa.Column(sa.Integer, nullable=False)
    id_path_details_malette = sa.Column(sa.Integer, nullable=False)
    path_details = relationship('PathDetails', foreign_keys=(id_path_details, id_path_details_malette))

    disabled = sa.Column(sa.Boolean, nullable=True)
    hotspot = sa.Column(sa.Boolean, nullable=True)

    __table_args__ = (
        sa.ForeignKeyConstraint(
            ['id_panorama', 'id_panorama_malette'],
            ['panorama.id_panorama', 'panorama.id_malette']),
        sa.ForeignKeyConstraint(
            ['id_path_details', 'id_path_details_malette'],
            ['path_details.id_path_details', 'path_details.id_malette']))


class PathDetails(Base):
    """ Describe a path """
    __tablename__ = "path_details"
    id_path_details = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    id_malette = sa.Column(sa.Integer, primary_key=True, default=get_malette_id())

    name = sa.Column(sa.String(70))
    decription = sa.Column(sa.String(250))

    id_start_node = sa.Column(sa.Integer, nullable=True)
    id_start_node_malette = sa.Column(sa.Integer, nullable=True)
    start_node = relationship(PathNode, foreign_keys=(id_start_node, id_start_node_malette))

    id_stop_node = sa.Column(sa.Integer, nullable=True)
    id_stop_node_malette = sa.Column(sa.Integer, nullable=True)
    stop_node = relationship(PathNode, foreign_keys=(id_stop_node, id_stop_node_malette))

    id_campaign = sa.Column(sa.Integer, nullable=False)
    id_campaign_malette = sa.Column(sa.Integer, nullable=False)
    campaign = relationship(Campaign, foreign_keys=(id_campaign, id_campaign_malette))

    __table_args__ = (
        sa.ForeignKeyConstraint(
            ['id_start_node', 'id_start_node_malette'],
            ['path_node.id_path_node', 'path_node.id_malette']),
        sa.ForeignKeyConstraint(
            ['id_stop_node', 'id_stop_node_malette'],
            ['path_node.id_path_node', 'path_node.id_malette']),
        sa.ForeignKeyConstraint(
            ['id_campaign', 'id_campaign_malette'],
            ['campaign.id_campaign', 'campaign.id_malette']))


class PathEdge(Base):
    """ Graph edges """
    __tablename__ = "path_edge"
    id_path_edge = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    id_malette = sa.Column(sa.Integer, primary_key=True, default=get_malette_id())

    source_id_path_node = sa.Column(sa.Integer, nullable=False)
    source_id_path_node_malette = sa.Column(sa.Integer, nullable=False)
    source_path_node = relationship(PathNode, foreign_keys=(source_id_path_node, source_id_path_node_malette))

    dest_id_path_node = sa.Column(sa.Integer, nullable=False)
    dest_id_path_node_malette = sa.Column(sa.Integer, nullable=False)
    dest_path_node = relationship(PathNode, foreign_keys=(dest_id_path_node, dest_id_path_node_malette))

    id_path_details = sa.Column(sa.Integer, nullable=False)
    id_path_details_malette = sa.Column(sa.Integer, nullable=False)
    path_details = relationship('PathDetails')

    __table_args__ = (
        sa.ForeignKeyConstraint(
            ['source_id_path_node', 'source_id_path_node_malette'],
            ['path_node.id_path_node', 'path_node.id_malette']),
        sa.ForeignKeyConstraint(
            ['dest_id_path_node', 'dest_id_path_node_malette'],
            ['path_node.id_path_node', 'path_node.id_malette']),
        sa.ForeignKeyConstraint(
            ['id_path_details', 'id_path_details_malette'],
            ['path_details.id_path_details', 'path_details.id_malette']))


class PathNodesExtended(Base):
    """ View of path_node with sensors data added """

    __table__ = view(
        'path_node_extended', Base.metadata,
        sa.select([
            PathNode.id_path_node, PathNode.id_malette, PathNode.id_panorama, PathNode.id_panorama_malette,
            PathNode.id_path_details, PathNode.id_path_details_malette, PathNode.disabled, PathNode.hotspot,
            Sensors.gps_pos, Sensors.degrees, Sensors.minutes, Sensors.id_sensors,
            Sensors.id_malette.label('id_sensors_malette')
        ]). \
            select_from(PathNode.__table__. \
            join(Panorama.__table__). \
            join(Cp.__table__). \
            join(Lot.__table__). \
            join(Sensors.__table__))
    )

    __table__.primary_key = [__table__.c.id_path_node, __table__.c.id_malette]

    __tablename__ = "path_node_extended"


# ---- Virtual tours, final render data for viewer/embed ----

class Virtualtour(Base):
    """ Virtualtour """
    __tablename__ = "virtualtour"
    id_virtualtour = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    id_malette = sa.Column(sa.Integer, primary_key=True, default=get_malette_id())

    title = sa.Column(sa.String(100))
    decription = sa.Column(sa.String(350))


class VirtualtourPath(Base):
    """ Path included in each virtual tours """
    __tablename__ = "virtualtour_path"
    id_virtualtour_path = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    id_malette = sa.Column(sa.Integer, primary_key=True, default=get_malette_id())

    id_virtualtour = sa.Column(sa.Integer, nullable=False)
    id_virtualtour_malette = sa.Column(sa.Integer, nullable=False)
    virtualtour = relationship(Virtualtour, foreign_keys=(id_virtualtour, id_virtualtour_malette))

    id_path_details = sa.Column(sa.Integer, nullable=False)
    id_path_details_malette = sa.Column(sa.Integer, nullable=False)
    path_details = relationship('PathDetails')

    __table_args__ = (
        sa.ForeignKeyConstraint(
            ['id_virtualtour', 'id_virtualtour_malette'],
            ['virtualtour.id_virtualtour', 'virtualtour.id_malette']),
        sa.ForeignKeyConstraint(
            ['id_path_details', 'id_path_details_malette'],
            ['path_details.id_path_details', 'path_details.id_malette']))


class VirtualtourHihlight(Base):
    """ Interesting points for the virtual tour """
    __tablename__ = "virtualtour_highlight"
    id_virtualtour_highlight = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    id_malette = sa.Column(sa.Integer, primary_key=True, default=get_malette_id())

    id_virtualtour = sa.Column(sa.Integer, nullable=False)
    id_virtualtour_malette = sa.Column(sa.Integer, nullable=False)
    virtualtour = relationship(Virtualtour, foreign_keys=(id_virtualtour, id_virtualtour_malette))

    id_path_node = sa.Column(sa.Integer, nullable=False)
    id_path_node_malette = sa.Column(sa.Integer, nullable=False)
    path_node = relationship(PathNode, foreign_keys=(id_path_node, id_path_node_malette))

    pitch = sa.Column(sa.Float)
    yaw = sa.Column(sa.Float)
    hfov = sa.Column(sa.Float)

    data = sa.Column(sa.String(900))

    virtualtour = relationship(Virtualtour, backref=backref('virtualtour'))

    __table_args__ = (
        sa.ForeignKeyConstraint(
            ['id_virtualtour', 'id_virtualtour_malette'],
            ['virtualtour.id_virtualtour', 'virtualtour.id_malette']),
        sa.ForeignKeyConstraint(
            ['id_path_node', 'id_path_node_malette'],
            ['path_node.id_path_node', 'path_node.id_malette']))

# !!! Please refer to README.md if you change this model to commit it (database is versionned) !!!
