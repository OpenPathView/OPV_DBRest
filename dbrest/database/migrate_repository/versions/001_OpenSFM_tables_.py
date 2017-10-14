from sqlalchemy import *
from migrate import *


from migrate.changeset import schema

from dbrest.helpers import get_malette_id

pre_meta = MetaData()
post_meta = MetaData()
path = Table('path', post_meta,
    Column('id_path', Integer, primary_key=True, autoincrement=True, nullable=False),
    Column('id_malette', Integer, primary_key=True, default=get_malette_id(), nullable=False),
    Column('id_shot_from', Integer, nullable=False),
    Column('id_shot_malette_from', Integer, nullable=False),
    Column('id_shot_to', Integer, nullable=False),
    Column('id_shot_malette_to', Integer, nullable=False),
    Column('active', Boolean, default=ColumnDefault(True)),
    Column('pitch', Float),
    Column('yaw', Float),
    Column('target_pitch', Float),
    Column('target_yaw', Float),
    Column('manual', Boolean, default=ColumnDefault(False)),
)

reconstruction = Table('reconstruction', post_meta,
    Column('id_reconstruction', Integer, primary_key=True, autoincrement=True, nullable=False),
    Column('id_malette', Integer, primary_key=True, default=get_malette_id(), nullable=False),
    Column('id_ref_lla', Integer, nullable=False),
    Column('id_ref_lla_malette', Integer, nullable=False),
    Column('raw_output_files', String(length=100), nullable=False),
    Column('reconstruction_algo', String(length=20), nullable=False),
    Column('id_campaign', Integer, nullable=False),
    Column('id_campaign_malette', Integer, nullable=False),
)

shot = Table('shot', post_meta,
    Column('id_shot', Integer, primary_key=True, autoincrement=True, nullable=False),
    Column('id_malette', Integer, primary_key=True, default=get_malette_id(), nullable=False),
    Column('orientation', Integer),
    Column('camera', String(length=250)),
    Column('gps_pos', ARRAY(Float(), dimensions=3), nullable=False),
    Column('gps_dop', Float),
    Column('rotation', ARRAY(Float(), dimensions=3), nullable=False),
    Column('translation', ARRAY(Float(), dimensions=3), nullable=False),
    Column('capture_time', Float),
    Column('id_reconstruction', Integer, nullable=False),
    Column('id_reconstruction_malette', Integer, nullable=False),
    Column('id_panorama', Integer, nullable=False),
    Column('id_panorama_malette', Integer, nullable=False),
    Column('id_corrected_sensors', Integer),
    Column('id_corrected_sensors_malette', Integer),
)


upgradefKeySQL = """
ALTER TABLE reconstruction
ADD CONSTRAINT reconstruction_id_campaign_fkey  FOREIGN KEY (id_campaign, id_campaign_malette)
                                                REFERENCES campaign(id_campaign, id_malette),
ADD CONSTRAINT reconstruction_id_ref_lla_fkey  FOREIGN KEY (id_ref_lla, id_ref_lla_malette)
                                               REFERENCES sensors(id_sensors, id_malette);

ALTER TABLE shot
ADD CONSTRAINT shot_id_reconstruction_fkey FOREIGN KEY (id_reconstruction, id_reconstruction_malette)
                                           REFERENCES reconstruction(id_reconstruction, id_malette),
ADD CONSTRAINT shot_id_panorama_fkey FOREIGN KEY (id_panorama, id_panorama_malette)
                                     REFERENCES panorama(id_panorama, id_malette),
ADD CONSTRAINT shot_id_corrected_sensors FOREIGN KEY (id_corrected_sensors,id_corrected_sensors_malette)
                                        REFERENCES sensors(id_sensors, id_malette);

ALTER TABLE path
ADD CONSTRAINT path_id_shot_from_fkey FOREIGN KEY (id_shot_from, id_shot_malette_from)
                                      REFERENCES shot(id_shot, id_malette),
ADD CONSTRAINT path_id_shot_to_fkey FOREIGN KEY (id_shot_to, id_shot_malette_to)
                                    REFERENCES shot(id_shot, id_malette);
"""

downgradefKeySQL = """
ALTER TABLE reconstruction
DROP CONSTRAINT reconstruction_id_campaign_fkey,
DROP CONSTRAINT reconstruction_id_ref_lla_fkey;

ALTER TABLE shot
DROP CONSTRAINT shot_id_reconstruction_fkey,
DROP CONSTRAINT shot_id_panorama_fkey,
DROP CONSTRAINT shot_id_corrected_sensors;

ALTER TABLE path
DROP CONSTRAINT path_id_shot_from_fkey,
DROP CONSTRAINT path_id_shot_to_fkey;
"""

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['path'].create()
    post_meta.tables['reconstruction'].create()
    post_meta.tables['shot'].create()

    migrate_engine.execute(upgradefKeySQL, multi=True)

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine

    migrate_engine.execute(downgradefKeySQL, multi=True)

    post_meta.tables['path'].drop()
    post_meta.tables['reconstruction'].drop()
    post_meta.tables['shot'].drop()
