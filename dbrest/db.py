import sqlalchemy as sa
from dbrest import models, settings
from dbrest.commons import CreateView
from sqlalchemy.orm import scoped_session, sessionmaker

engine = sa.create_engine(settings.engine_path)
session = scoped_session(sessionmaker(bind=engine))

# Create DB model
def create_all():
    # mapping views
    sa.orm.mapper(models.PathNodesExtended, models.PathNodesExtended.__view__)

    # creating schema (not including views)
    models.Base.metadata.create_all(engine)

    # Creating the views
    engine.execute(CreateView(models.PathNodesExtended))

