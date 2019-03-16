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
    Column('active', Boolean, nullable=True),
    Column('id_sensors_reconstructed', Integer, nullable=True),
    Column('id_sensors_reconstructed_malette', Integer, nullable=True),
    Column('has_hole', Boolean, nullable=True, default=ColumnDefault(False)),
)

lot = Table('lot', post_meta,
    Column('id_lot', Integer, primary_key=True, nullable=False),
    Column('id_malette', Integer, primary_key=True, nullable=False),
    Column('pictures_path', String(length=100), nullable=False),
    Column('goprofailed', Integer, nullable=False),
    Column('takenDate', DateTime, nullable=False),
    Column('active', Boolean),
    Column('id_sensors', Integer, nullable=False),
    Column('id_sensors_malette', Integer, nullable=False),
    Column('id_campaign', Integer, nullable=False),
    Column('id_campaign_malette', Integer, nullable=False),
    Column('id_tile', Integer),
    Column('id_tile_malette', Integer),
    Column('is_blur', Boolean, default=ColumnDefault(False)),
)

upgrade_view = """
DROP VIEW panorama_sensors;
CREATE VIEW public.panorama_sensors AS
    SELECT panorama.id_panorama,
    panorama.id_malette,
    panorama.has_hole,
    cp.id_cp,
    cp.id_malette AS id_cp_malette,
    panorama.active,
    panorama.equirectangular_path,
    panorama.is_photosphere,
    sensors_1.id_sensors AS reconstructed_id_sensors,
    sensors_1.id_malette AS reconstructed_id_malette,
    sensors_1.gps_pos AS reconstructed_gps_pos,
    sensors_1.degrees AS reconstructed_degrees,
    sensors_1.minutes AS reconstructed_minutes,
    sensors_2.id_sensors AS original_id_sensors,
    sensors_2.id_malette AS original_id_malette,
    sensors_2.gps_pos AS original_gps_pos,
    sensors_2.degrees AS original_degrees,
    sensors_2.minutes AS original_minutes,
    campaign.id_campaign,
    campaign.id_malette AS id_campaign_malette
   FROM panorama
     LEFT JOIN sensors sensors_1 ON panorama.id_sensors_reconstructed = sensors_1.id_sensors AND panorama.id_sensors_reconstructed_malette = sensors_1.id_malette
     JOIN cp ON cp.id_cp = panorama.id_cp AND cp.id_malette = panorama.id_cp_malette
     JOIN lot ON lot.id_lot = cp.id_lot AND lot.id_malette = cp.id_lot_malette
     JOIN campaign ON campaign.id_campaign = lot.id_campaign AND campaign.id_malette = lot.id_campaign_malette
     JOIN sensors sensors_2 ON lot.id_sensors = sensors_2.id_sensors AND lot.id_sensors_malette = sensors_2.id_malette;
"""

downgrade_view = """
DROP VIEW panorama_sensors;
CREATE VIEW public.panorama_sensors AS
    SELECT panorama.id_panorama,
    panorama.id_malette,
    cp.id_cp,
    cp.id_malette AS id_cp_malette,
    panorama.active,
    panorama.equirectangular_path,
    panorama.is_photosphere,
    sensors_1.id_sensors AS reconstructed_id_sensors,
    sensors_1.id_malette AS reconstructed_id_malette,
    sensors_1.gps_pos AS reconstructed_gps_pos,
    sensors_1.degrees AS reconstructed_degrees,
    sensors_1.minutes AS reconstructed_minutes,
    sensors_2.id_sensors AS original_id_sensors,
    sensors_2.id_malette AS original_id_malette,
    sensors_2.gps_pos AS original_gps_pos,
    sensors_2.degrees AS original_degrees,
    sensors_2.minutes AS original_minutes,
    campaign.id_campaign,
    campaign.id_malette AS id_campaign_malette
   FROM panorama
     LEFT JOIN sensors sensors_1 ON panorama.id_sensors_reconstructed = sensors_1.id_sensors AND panorama.id_sensors_reconstructed_malette = sensors_1.id_malette
     JOIN cp ON cp.id_cp = panorama.id_cp AND cp.id_malette = panorama.id_cp_malette
     JOIN lot ON lot.id_lot = cp.id_lot AND lot.id_malette = cp.id_lot_malette
     JOIN campaign ON campaign.id_campaign = lot.id_campaign AND campaign.id_malette = lot.id_campaign_malette
     JOIN sensors sensors_2 ON lot.id_sensors = sensors_2.id_sensors AND lot.id_sensors_malette = sensors_2.id_malette;
"""

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine

    post_meta.tables['panorama'].columns['has_hole'].create()
    post_meta.tables['lot'].columns['is_blur'].create()

    migrate_engine.execute(upgrade_view, multi=True)


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    
    post_meta.tables['panorama'].columns['has_hole'].drop()
    post_meta.tables['lot'].columns['is_blur'].drop()

    migrate_engine.execute(downgrade_view, multi=True)

