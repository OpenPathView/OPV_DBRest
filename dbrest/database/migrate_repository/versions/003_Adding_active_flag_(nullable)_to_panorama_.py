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
    Column('active', Boolean, nullable=True)
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['panorama'].columns['active'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['panorama'].columns['active'].drop()
