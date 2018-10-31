from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
path_details = Table('path_details', pre_meta,
    Column('id_path_details', INTEGER, primary_key=True, nullable=False),
    Column('id_malette', INTEGER, primary_key=True, nullable=False),
    Column('name', VARCHAR(length=70)),
    Column('decription', VARCHAR(length=250)),
    Column('id_start_node', INTEGER),
    Column('id_start_node_malette', INTEGER),
    Column('id_stop_node', INTEGER),
    Column('id_stop_node_malette', INTEGER),
    Column('id_campaign', INTEGER, nullable=False),
    Column('id_campaign_malette', INTEGER, nullable=False),
)

path_node = Table('path_node', post_meta,
    Column('id_path_node', Integer, primary_key=True, nullable=False),
    Column('id_malette', Integer, primary_key=True, nullable=False),
    Column('id_panorama', Integer, nullable=False),
    Column('id_panorama_malette', Integer, nullable=False),
    Column('id_path_details', Integer, nullable=False),
    Column('id_path_details_malette', Integer, nullable=False),
    Column('disabled', Boolean),
    Column('hotspot', Boolean),
    Column('endpoint', Boolean),
)

upgradefKeySQL = """
ALTER TABLE path_details
DROP CONSTRAINT path_details_id_start_node_fkey,
DROP CONSTRAINT path_details_id_stop_node_fkey;

DROP VIEW path_node_extended;
CREATE VIEW public.path_node_extended AS
    SELECT path_node.id_path_node,
    path_node.id_malette,
    panorama.id_panorama,
    panorama.id_malette AS id_panorama_malette,
    path_details.id_path_details,
    path_details.id_malette AS id_path_details_malette,
    path_node.disabled,
    path_node.hotspot,
    path_node.endpoint,
    sensors_1.id_sensors AS reconstructed_id_sensors,
    sensors_1.id_malette AS reconstructed_id_malette,
    sensors_1.gps_pos AS reconstructed_gps_pos,
    sensors_1.degrees AS reconstructed_degrees,
    sensors_1.minutes AS reconstructed_minutes,
    sensors_2.id_sensors AS original_id_sensors,
    sensors_2.id_malette AS original_id_malette,
    sensors_2.gps_pos AS original_gps_pos,
    sensors_2.degrees AS original_degrees,
    sensors_2.minutes AS original_minutes
   FROM path_node
     JOIN path_details ON path_details.id_path_details = path_node.id_path_details AND path_details.id_malette = path_node.id_path_details_malette
     JOIN panorama ON panorama.id_panorama = path_node.id_panorama AND panorama.id_malette = path_node.id_panorama_malette
     LEFT JOIN sensors sensors_1 ON panorama.id_sensors_reconstructed = sensors_1.id_sensors AND panorama.id_sensors_reconstructed_malette = sensors_1.id_malette
     JOIN cp ON cp.id_cp = panorama.id_cp AND cp.id_malette = panorama.id_cp_malette
     JOIN lot ON lot.id_lot = cp.id_lot AND lot.id_malette = cp.id_lot_malette
     JOIN sensors sensors_2 ON lot.id_sensors = sensors_2.id_sensors AND lot.id_sensors_malette = sensors_2.id_malette;
"""

downgradefKeySQL = """
ALTER TABLE path_details
ADD CONSTRAINT path_details_id_start_node_fkey  FOREIGN KEY (id_start_node, id_start_node_malette)
                                                REFERENCES path_node(id_path_node, id_malette),
ADD CONSTRAINT path_details_id_stop_node_fkey  FOREIGN KEY (id_stop_node, id_stop_node_malette)
                                               REFERENCES path_node(id_path_node, id_malette);
                                               
DROP VIEW path_node_extended;
CREATE VIEW public.path_node_extended AS
    SELECT path_node.id_path_node,
    path_node.id_malette,
    panorama.id_panorama,
    panorama.id_malette AS id_panorama_malette,
    path_details.id_path_details,
    path_details.id_malette AS id_path_details_malette,
    path_node.disabled,
    path_node.hotspot,
    sensors_1.id_sensors AS reconstructed_id_sensors,
    sensors_1.id_malette AS reconstructed_id_malette,
    sensors_1.gps_pos AS reconstructed_gps_pos,
    sensors_1.degrees AS reconstructed_degrees,
    sensors_1.minutes AS reconstructed_minutes,
    sensors_2.id_sensors AS original_id_sensors,
    sensors_2.id_malette AS original_id_malette,
    sensors_2.gps_pos AS original_gps_pos,
    sensors_2.degrees AS original_degrees,
    sensors_2.minutes AS original_minutes
   FROM path_node
     JOIN path_details ON path_details.id_path_details = path_node.id_path_details AND path_details.id_malette = path_node.id_path_details_malette
     JOIN panorama ON panorama.id_panorama = path_node.id_panorama AND panorama.id_malette = path_node.id_panorama_malette
     LEFT JOIN sensors sensors_1 ON panorama.id_sensors_reconstructed = sensors_1.id_sensors AND panorama.id_sensors_reconstructed_malette = sensors_1.id_malette
     JOIN cp ON cp.id_cp = panorama.id_cp AND cp.id_malette = panorama.id_cp_malette
     JOIN lot ON lot.id_lot = cp.id_lot AND lot.id_malette = cp.id_lot_malette
     JOIN sensors sensors_2 ON lot.id_sensors = sensors_2.id_sensors AND lot.id_sensors_malette = sensors_2.id_malette;
"""


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine

    migrate_engine.execute(upgradefKeySQL, multi=True)

    pre_meta.tables['path_details'].columns['id_start_node'].drop()
    pre_meta.tables['path_details'].columns['id_start_node_malette'].drop()
    pre_meta.tables['path_details'].columns['id_stop_node'].drop()
    pre_meta.tables['path_details'].columns['id_stop_node_malette'].drop()
    post_meta.tables['path_node'].columns['endpoint'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['path_details'].columns['id_start_node'].create()
    pre_meta.tables['path_details'].columns['id_start_node_malette'].create()
    pre_meta.tables['path_details'].columns['id_stop_node'].create()
    pre_meta.tables['path_details'].columns['id_stop_node_malette'].create()
    post_meta.tables['path_node'].columns['endpoint'].drop()

    migrate_engine.execute(downgradefKeySQL, multi=True)
