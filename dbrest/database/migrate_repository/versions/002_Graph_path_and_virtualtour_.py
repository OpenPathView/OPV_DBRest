from sqlalchemy import *
from migrate import *

from dbrest.helpers import get_malette_id

from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
path_details = Table('path_details', post_meta,
    Column('id_path_details', Integer, primary_key=True, nullable=False, autoincrement=True),
    Column('id_malette', Integer, primary_key=True, nullable=False, default=get_malette_id()),
    Column('name', String(length=70)),
    Column('decription', String(length=250)),
    Column('id_start_node', Integer, nullable=True),
    Column('id_start_node_malette', Integer, nullable=True),
    Column('id_stop_node', Integer, nullable=True),
    Column('id_stop_node_malette', Integer, nullable=True),
    Column('id_campaign', Integer, nullable=False),
    Column('id_campaign_malette', Integer, nullable=False),
)

path_edge = Table('path_edge', post_meta,
    Column('id_path_edge', Integer, primary_key=True, nullable=False, autoincrement=True),
    Column('id_malette', Integer, primary_key=True, nullable=False, default=get_malette_id()),
    Column('source_id_path_node', Integer, nullable=False),
    Column('source_id_path_node_malette', Integer, nullable=False),
    Column('dest_id_path_node', Integer, nullable=False),
    Column('dest_id_path_node_malette', Integer, nullable=False),
    Column('id_path_details', Integer, nullable=False),
    Column('id_path_details_malette', Integer, nullable=False),
)

path_node = Table('path_node', post_meta,
    Column('id_path_node', Integer, primary_key=True, nullable=False, autoincrement=True),
    Column('id_malette', Integer, primary_key=True, nullable=False, default=get_malette_id()),
    Column('id_panorama', Integer, nullable=False),
    Column('id_panorama_malette', Integer, nullable=False),
    Column('id_path_details', Integer, nullable=False),
    Column('id_path_details_malette', Integer, nullable=False),
    Column('disabled', Boolean),
    Column('hotspot', Boolean),
)

virtualtour = Table('virtualtour', post_meta,
    Column('id_virtualtour', Integer, primary_key=True, nullable=False, autoincrement=True),
    Column('id_malette', Integer, primary_key=True, nullable=False, default=get_malette_id()),
    Column('title', String(length=100)),
    Column('decription', String(length=350)),
)

virtualtour_highlight = Table('virtualtour_highlight', post_meta,
    Column('id_virtualtour_highlight', Integer, primary_key=True, nullable=False, autoincrement=True),
    Column('id_malette', Integer, primary_key=True, nullable=False, default=get_malette_id()),
    Column('id_virtualtour', Integer, nullable=False),
    Column('id_virtualtour_malette', Integer, nullable=False),
    Column('id_path_node', Integer, nullable=False),
    Column('id_path_node_malette', Integer, nullable=False),
    Column('pitch', Float),
    Column('yaw', Float),
    Column('hfov', Float),
    Column('data', String(length=900)),
)

virtualtour_path = Table('virtualtour_path', post_meta,
    Column('id_virtualtour_path', Integer, primary_key=True, nullable=False, autoincrement=True),
    Column('id_malette', Integer, primary_key=True, nullable=False, default=get_malette_id()),
    Column('id_virtualtour', Integer, nullable=False),
    Column('id_virtualtour_malette', Integer, nullable=False),
    Column('id_path_details', Integer, nullable=False),
    Column('id_path_details_malette', Integer, nullable=False),
)

upgradefKeySQL = """
ALTER TABLE path_node
ADD CONSTRAINT path_node_id_panorama_fkey  FOREIGN KEY (id_panorama, id_panorama_malette)
                                                REFERENCES panorama(id_panorama, id_malette),
ADD CONSTRAINT path_node_id_path_details_fkey  FOREIGN KEY (id_path_details, id_path_details_malette)
                                               REFERENCES path_details(id_path_details, id_malette);

ALTER TABLE path_details
ADD CONSTRAINT path_details_id_start_node_fkey  FOREIGN KEY (id_start_node, id_start_node_malette)
                                                REFERENCES path_node(id_path_node, id_malette),
ADD CONSTRAINT path_details_id_campaign_fkey  FOREIGN KEY (id_campaign, id_campaign_malette)
                                                REFERENCES campaign(id_campaign, id_malette),
ADD CONSTRAINT path_details_id_stop_node_fkey  FOREIGN KEY (id_stop_node, id_stop_node_malette)
                                               REFERENCES path_node(id_path_node, id_malette);
                                               
ALTER TABLE path_edge
ADD CONSTRAINT path_edge_source_id_path_node_fkey  FOREIGN KEY (source_id_path_node, source_id_path_node_malette)
                                                REFERENCES path_node(id_path_node, id_malette),
ADD CONSTRAINT path_edge_dest_id_path_node_fkey  FOREIGN KEY (dest_id_path_node, dest_id_path_node_malette)
                                                REFERENCES path_node(id_path_node, id_malette),
ADD CONSTRAINT path_edge_id_path_details_fkey  FOREIGN KEY (id_path_details, id_path_details_malette)
                                               REFERENCES path_details(id_path_details, id_malette);
                                               
ALTER TABLE virtualtour_path
ADD CONSTRAINT virtualtour_path_id_virtualtour_fkey  FOREIGN KEY (id_virtualtour, id_virtualtour_malette)
                                                REFERENCES virtualtour(id_virtualtour, id_malette),
ADD CONSTRAINT virtualtour_path_id_path_details_fkey  FOREIGN KEY (id_path_details, id_path_details_malette)
                                               REFERENCES path_details(id_path_details, id_malette);
                                               
ALTER TABLE virtualtour_highlight
ADD CONSTRAINT virtualtour_highlight_id_virtualtour_fkey  FOREIGN KEY (id_virtualtour, id_virtualtour_malette)
                                                REFERENCES virtualtour(id_virtualtour, id_malette),
ADD CONSTRAINT virtualtour_highlight_id_path_node_fkey  FOREIGN KEY (id_path_node, id_path_node_malette)
                                               REFERENCES path_node(id_path_node, id_malette);
"""

create_view = """
CREATE VIEW public.path_node_extended AS
 SELECT path_node.id_path_node,
    path_node.id_malette,
    path_node.id_panorama,
    path_node.id_panorama_malette,
    path_node.id_path_details,
    path_node.id_path_details_malette,
    path_node.disabled,
    path_node.hotspot,
    public.st_asgeojson(sensors.gps_pos) AS gps_pos,
    sensors.degrees,
    sensors.minutes,
    sensors.id_sensors,
    sensors.id_malette AS id_sensors_malette
   FROM ((((public.path_node
     JOIN public.panorama ON (((panorama.id_panorama = path_node.id_panorama) AND (panorama.id_malette = path_node.id_panorama_malette))))
     JOIN public.cp ON (((cp.id_cp = panorama.id_cp) AND (cp.id_malette = panorama.id_cp_malette))))
     JOIN public.lot ON (((lot.id_lot = cp.id_lot) AND (lot.id_malette = cp.id_lot_malette))))
     JOIN public.sensors ON (((sensors.id_sensors = lot.id_sensors) AND (sensors.id_malette = lot.id_sensors_malette))));
"""

drop_view = """
DROP VIEW path_node_extended;
"""

downgradefKeySQL = """
ALTER TABLE path_node
DROP CONSTRAINT path_node_id_panorama_fkey,
DROP CONSTRAINT path_node_id_path_details_fkey;

ALTER TABLE path_details
DROP CONSTRAINT path_details_id_start_node_fkey,
DROP CONSTRAINT path_details_id_campaign_fkey,
DROP CONSTRAINT path_details_id_stop_node_fkey;

ALTER TABLE path_edge
DROP CONSTRAINT path_edge_source_id_path_node_fkey,
DROP CONSTRAINT path_edge_dest_id_path_node_fkey,
DROP CONSTRAINT path_details_id_stop_node_fkey;

ALTER TABLE virtualtour_path
DROP CONSTRAINT virtualtour_path_id_virtualtour_fkey,
DROP CONSTRAINT virtualtour_path_id_path_details_fkey;

ALTER TABLE virtualtour_highlight
DROP CONSTRAINT virtualtour_highlight_id_virtualtour_fkey,
DROP CONSTRAINT virtualtour_highlight_id_path_node_fkey;
"""

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['path_details'].create()
    post_meta.tables['path_edge'].create()
    post_meta.tables['path_node'].create()
    post_meta.tables['virtualtour'].create()
    post_meta.tables['virtualtour_highlight'].create()
    post_meta.tables['virtualtour_path'].create()

    migrate_engine.execute(upgradefKeySQL, multi=True)
    migrate_engine.execute(create_view, multi=True)


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine

    migrate_engine.execute(downgradefKeySQL, multi=True)
    migrate_engine.execute(drop_view, multi=True)

    post_meta.tables['path_details'].drop()
    post_meta.tables['path_edge'].drop()
    post_meta.tables['path_node'].drop()
    post_meta.tables['virtualtour'].drop()
    post_meta.tables['virtualtour_highlight'].drop()
    post_meta.tables['virtualtour_path'].drop()
