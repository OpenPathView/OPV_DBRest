from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()

# See https://github.com/OpenPathView/OPV_DBRest/issues/56#issuecomment-434255649
upgrade_view = """
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

downgrade_view = """
DROP VIEW panorama_sensors;
CREATE VIEW public.panorama_sensors AS
    SELECT panorama.id_panorama,
        panorama.id_malette,
        panorama.id_cp,
        panorama.id_cp_malette,
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

DROP VIEW path_node_extended;

CREATE VIEW public.path_node_extended AS
    SELECT path_node.id_path_node,
        path_node.id_malette,
        path_node.id_panorama,
        path_node.id_panorama_malette,
        path_node.id_path_details,
        path_node.id_path_details_malette,
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

    migrate_engine.execute(upgrade_view, multi=True)


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine

    migrate_engine.execute(downgrade_view, multi=True)
