from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
panorama = Table('panorama', post_meta,
    Column('id_panorama', Integer, primary_key=True, nullable=False),
    Column('id_malette', Integer, primary_key=True, nullable=False),
    Column('equirectangular_path', String(length=100)),
    Column('is_photosphere', Boolean, default=ColumnDefault(False)),
    Column('id_cp', Integer, nullable=False),
    Column('id_cp_malette', Integer, nullable=False),
    Column('active', Boolean),
    Column('id_sensors_reconstructed', Integer, nullable=True),
    Column('id_sensors_reconstructed_malette', Integer, nullable=True),
)

upgradefKeySQL = """
ALTER TABLE panorama
ADD CONSTRAINT panorama_id_sensors_reconstructed_fkey  FOREIGN KEY (id_sensors_reconstructed, id_sensors_reconstructed_malette)
                                                REFERENCES sensors(id_sensors, id_malette);
"""

downgradefKeySQL = """
ALTER TABLE panorama
DROP CONSTRAINT panorama_id_sensors_reconstructed_fkey;
"""

upgradeView = """
DROP VIEW public.path_node_extended;

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
    sensors.id_malette AS id_sensors_malette,
    panorama.id_sensors_reconstructed AS id_sensors_reconstructed,
    panorama.id_sensors_reconstructed_malette AS id_sensors_reconstructed_malette
   FROM ((((public.path_node
     JOIN public.panorama ON (((panorama.id_panorama = path_node.id_panorama) AND (panorama.id_malette = path_node.id_panorama_malette))))
     JOIN public.sensors ON (((sensors.id_sensors = panorama.id_sensors_reconstructed) AND (sensors.id_malette = panorama.id_sensors_reconstructed_malette))))
   ));
"""

downgradeView = """
DROP VIEW public.path_node_extended;

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

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['panorama'].columns['id_sensors_reconstructed'].create()
    post_meta.tables['panorama'].columns['id_sensors_reconstructed_malette'].create()

    migrate_engine.execute(upgradefKeySQL, multi=True)
    migrate_engine.execute(upgradeView, multi=True)


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['panorama'].columns['id_sensors_reconstructed'].drop()
    post_meta.tables['panorama'].columns['id_sensors_reconstructed_malette'].drop()

    migrate_engine.execute(downgradeView, multi=True)
    migrate_engine.execute(downgradefKeySQL, multi=True)
