import sqlalchemy as sa
from dbrest import models, settings
from sqlalchemy.orm import scoped_session, sessionmaker

engine = sa.create_engine(settings.engine_path)
session = scoped_session(sessionmaker(bind=engine))

# Create DB model
def create_all():
    models.Base.metadata.create_all(engine)
