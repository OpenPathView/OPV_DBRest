import hug
import hug.middleware
from falcon import HTTP_400, HTTP_201

import json

from sqlalchemy import func
from sqlalchemy.inspection import inspect as sainspect
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from dbrest import schema, models, settings, db

import logging
from dbrest.helpers.logging import setup_logging

print("Config : ")
print("Database :", settings.engine_path)
print("Debug :", str(settings.debug))
print("IDMalette :", settings.IDMalette)

# -- logger --
setup_logging()
logging.getLogger("dbrest").setLevel(logging.DEBUG if settings.debug else logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Starting dbrest API with IDMalette : %r", settings.IDMalette)
logger.debug("OPV API is in debug mode")
logger.debug("OPV API is using this database : %r", settings.engine_path)

api = hug.API(__name__)

api.http.add_middleware(hug.middleware.CORSMiddleware(api, ['*']))


def generate_accessors(schm, version=1, name=None):
    """Will generate GET, POST and PUT/PATCH for the model contained by the schema

    Args:
        schem: a marshmallow-sqlalchemy's Schema instance
        path (str): the path where you will find the ressource if path is None, will use the __tablename__ of the model
        name: A custom name that will be used the path
        version (int): the version of the ressource
    """
    model = schm.Meta.model
    model_name = model.__tablename__ if not name else name

    mapper = sainspect(model)
    pks = mapper.primary_key
    pks_name = tuple(pk.name for pk in pks)

    # /model_name
    path_get_all = "/{}".format(model_name)
    # /model_name/pk1/pk2/.../pkn
    path_get_one = path_get_all + "/{" + "}/{".join(pks_name) + "}"
    path_post = path_get_all
    path_put = path_get_one
    path_delete = path_get_one
    path_delete_all = path_get_all

    def cant_find_ress(kwargs):
        pks_d = {pk: kwargs.get(pk) for pk in pks_name}
        logger.error("Can't find ressource : %r", pks_d)
        return "Can't find any ressource with " + ", ".join("{}={}".format(pk, val) for pk, val in pks_d.items())

    # 1. Create a general get, without any doc
    def get_all(response, **kwargs):
        # Return all instances of the ressource
        logger.debug("Call to get severeals ressources : %r", kwargs)
        insts = schm.filter_instances(kwargs)
        d = schm.dump(insts, many=True).data
        logger.debug("Returning the following ressources : %r", d)
        return d

    def get_one(response, **kwargs):
        # return only one instance of the ressource, according to the pks
        # treat kwarks according pks
        # Get the instance of the model
        logger.debug("Request only one ressource : %r", kwargs)
        try:
            inst = schm.get_instance(kwargs)
        except SQLAlchemyError as err:
            logger.error("Error while getting the requested ressource : %r", err)
            schm.Meta.sqla_session.rollback()
            inst = None

        if not inst:
            response.status = HTTP_400
            logger.debug("Nothing found returning status 400")
            return cant_find_ress(kwargs)

        d = schm.dump(inst).data  # get a JSON using marshmallow
        logger.debug("Returning the founded ressource : %r", d)
        return d

    # 2. Add documentation following a template
    get_one.__doc__ = """Allow to get a {} ressource.""".format(model_name, pks_name)
    get_all.__doc__ = """Allow to get all {} ressources.
    If filters are specified, you can get only a part of the query.
    e.g: .../campaign?id_malette==1 will return every instances of campaign where id_malette==1""".format(model_name)

    # 3. Say to hug that it exists
    hug.get(path_get_one)(get_one)
    hug.get(path_get_all)(get_all)

    # And do the same for POSTs requests
    def post(response, **kwargs):

        logger.debug("Received POST request : %r", kwargs)
        inst, error = schm.load(kwargs)  # create ress in mem
        logger.debug("Created in memory instance of the ressource : %r", inst)

        if error:
            logger.error("Returning 400 status. Something went wrong when creating in memory instance of the ressource based on SQLAlchemy Schema : %r", error)
            response.status = HTTP_400
            return error

        try:
            logger.debug("Trying to commit the new ressource : %r", inst)
            schm.Meta.sqla_session.add(inst)  # add inst to server
            schm.Meta.sqla_session.commit()  # commit to server
            logger.debug("Succesfully commited new ressource : %r", inst)
        except IntegrityError as err:
            schm.Meta.sqla_session.rollback()  # uncommit ! It doesn't works ! :-(
            response.status = HTTP_400
            logger.error("Got IntegrityError from SQLAlchemy : %r", err)
            logger.debug("Returning 400 error.")
            return "IntegrityError ! {}".format(err.args)
        except SQLAlchemyError as err:
            schm.Meta.sqla_session.rollback()  # uncommit ! It doesn't works ! :-(
            response.status = HTTP_400
            logger.error("SQLAclhemy failled when commiting new ressource with following error : %r", err)
            return "Sqlalchemy didn't like it {}".format(err.__class__)

        response.status = HTTP_201
        d = schm.dump(inst).data
        logger.debug("Returning inserted ressource datas : %r", d)
        return schm.dump(inst).data

    post.__doc__ = "Allow to create a new {} ressource".format(model_name)

    hug.post(path_post)(post)

    # And do the same for PUT/PATCHs requests
    def put(response, **kwargs):
        logger.debug("PUT call : %r", kwargs)

        # Find ress
        try:
            logger.debug("Trying to find the ressource that needs to be updated")
            inst = schm.get_instance(kwargs)
        except SQLAlchemyError as err:
            logger.error("SQLAlchemy error while trying to find the ressource for put : %r", err)
            schm.Meta.sqla_session.rollback()  # uncommit ! It doesn't works ! :-(
            inst = None

        if inst is None:
            logger.error("No ressource found for PUT returning 400 status.")
            response.status = HTTP_400
            return cant_find_ress(kwargs)

        # update ressource data
        old_data = schm.dump(inst).data
        old_data.update(kwargs)

        logger.debug("Updating data in memory using SQLAlchemy schema")
        data, error = schm.load(old_data, instance=inst)  # set data in mem

        if error:
            logger.error("Error occured when update ressource with request data in memory based on SQLAlchemy schema : %r", error)
            response.status = HTTP_400
            return error

        try:
            schm.Meta.sqla_session.commit()  # commit to serv
            logger.debug("Ressource succesfully commited to database")
        except SQLAlchemyError as err:
            logger.error("Error when commiting updated resource : %r", err)
            schm.Meta.sqla_session.rollback()  # uncommit ! It doesn't works ! :-(
            response.status = HTTP_400
            return "Sqlalchemy didn't like it {}".format(err.args)

        d = schm.dump(inst).data
        logger.debug("Returning updated ressource : %r", d)
        return d

    put.__doc__ = "Allow to modify a new {} ressource".format(model_name)

    hug.put(path_put)(put)
    hug.patch(path_put)(put)

    # DELETE ressource
    def delete_one(response, **kwargs):
        logger.debug("DELETE call : %r", kwargs)

        # Find ress and delete
        try:
            logger.debug("Trying to find the ressource that needs to be updated")
            inst = schm.get_instance(kwargs)
            schm.Meta.sqla_session.delete(inst)
            schm.Meta.sqla_session.commit()  # commit to serv
        except SQLAlchemyError as err:
            logger.error("SQLAlchemy error while trying to find the ressource for delete : %r", err)
            schm.Meta.sqla_session.rollback()  # uncommit ! It doesn't works ! :-(
            inst = None
            return "SQLAlchemy error while trying to find the ressource for delete : %r" % err

        if inst is None:
            logger.error("No ressource found for PUT returning 400 status.")
            response.status = HTTP_400
            return cant_find_ress(kwargs)

        return {}

    hug.delete(path_delete)(delete_one)

    def delete_all(response, **kwargs):
        # Return all instances of the ressource
        logger.debug("Call to delete severeals ressources : %r", kwargs)
        insts = schm.filter_instances(kwargs)
        try:
            for inst in insts:
                schm.Meta.sqla_session.delete(inst)
            schm.Meta.sqla_session.commit()  # commit to serv
        except SQLAlchemyError as err:
            logger.error("SQLAlchemy error while trying to find the ressource for delete : %r", err)
            schm.Meta.sqla_session.rollback()  # uncommit ! It doesn't works ! :-(
            return "SQLAlchemy error while trying to find the ressource for delete : %r" % err

        return None

    hug.delete(path_delete_all)(delete_all)

@hug.get("/sensors/{id_sensors}/{id_malette}/within/{n}", version=1)
def within(id_malette, id_sensors, n: hug.types.number, response):
    """return all the sensors within {n} meters to sensors(id_sensors, id_malette)"""
    logger.debug("Call to within with : id_malette: %r, id_sensors: %r, distance: %r ", id_malette, id_sensors, n)
    schm = schema.SensorsSchema()
    ids = {"id_malette": id_malette, "id_sensors": id_sensors}

    try:
        inst = schm.get_instance(ids)
    except SQLAlchemyError as err:
        logger.error("Error when getting sensor from db : %r", err)
        schm.Meta.sqla_session.rollback()
        inst = None

    if not inst:
        response.status = HTTP_400
        logger.debug("Returning 400 status")
        return "Can't find sensors"

    geom = json.dumps(inst.gps_pos)

    try:
        logger.debug("Searching sensors in the defined zone (distance %r, around %r)", n, geom)
        insts = schm.Meta.sqla_session.query(models.Sensors).filter(
            func.ST_DWithin(
                func.ST_GeomFromGeoJSON(geom),
                models.Sensors.gps_pos,
                n)
        )
    except SQLAlchemyError as err:
        logger.error("Error when requesting sensor in the disance zone : %r", err)
        schm.Meta.sqla_session.rollback()
        insts = None

    d = schm.dump(insts, many=True).data
    logger.debug("Returning theses sensors : %r", d)
    return d


# db.create_all()  # No more needed has the database needs to be upgraded before

generate_accessors(schema.CampaignSchema())
generate_accessors(schema.PanoramaSchema())
generate_accessors(schema.SensorsSchema())
generate_accessors(schema.TileSchema())
generate_accessors(schema.LotSchema())
generate_accessors(schema.LotWithSensorsSchema(), name='lot/with_sensors')
generate_accessors(schema.CpSchema())
generate_accessors(schema.PanoramaSensorsSchema())
generate_accessors(schema.TrackEdgeSchema())
generate_accessors(schema.ReconstructionSchema())
generate_accessors(schema.ShotSchema())
generate_accessors(schema.PathSchema())
generate_accessors(schema.PathNodeSchema())
generate_accessors(schema.PathDetailsSchema())
generate_accessors(schema.PathEdgeSchema())
generate_accessors(schema.PathNodeExtendedSchema())
generate_accessors(schema.VirtualtourSchema())
generate_accessors(schema.VirtualtourPathSchema())
generate_accessors(schema.VirtualtourHighlightSchema())
