import hug
from falcon import HTTP_400, HTTP_201

import json

from sqlalchemy import func
from sqlalchemy.inspection import inspect as sainspect
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from dbrest import schema, models, settings

print("Config : ")
print("Database : " + settings.engine_path)
print("Debug : " + str(settings.debug))
print("rederbroID : " + settings.rederbroID)

def generate_accessors(schm, version=1):
    """Will generate GET, POST and PUT/PATCH for the model contained by the schema

    Args:
        schem: a marshmallow-sqlalchemy's Schema instance
        path (str): the path where you will find the ressource if path is None, will use the __tablename__ of the model
        version (int): the version of the ressource
    """
    model = schm.Meta.model
    model_name = model.__tablename__

    mapper = sainspect(model)
    pks = mapper.primary_key
    pks_name = tuple(pk.name for pk in pks)

    # /model_name
    path_get_all = "/{}".format(model_name)
    # /model_name/pk1/pk2/.../pkn
    path_get_one = path_get_all + "/{" + "}/{".join(pks_name) + "}"
    path_post = path_get_all
    path_put = path_get_one

    def cant_find_ress(kwargs):
        pks_d = {pk: kwargs.get(pk) for pk in pks_name}
        return "Can't find any ressource with " + ", ".join("{}={}".format(pk, val) for pk, val in pks_d.items())

    # 1. Create a general get, without any doc
    def get_all(response, **kwargs):
        # Return all instances of the ressource
        insts = schm.filter_instances(kwargs)
        return schm.dump(insts, many=True).data

    def get_one(response, **kwargs):
        # return only one instance of the ressource, according to the pks
        # treat kwarks according pks
        # Get the instance of the model
        try:
            inst = schm.get_instance(kwargs)
        except SQLAlchemyError:
            schm.Meta.sqla_session.rollback()
            inst = None

        if not inst:
            response.status = HTTP_400
            return cant_find_ress(kwargs)

        return schm.dump(inst).data  # get a JSON using marshmallow

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
        inst, error = schm.load(kwargs)  # create ress in mem

        if error:
            response.status = HTTP_400
            return error

        try:
            schm.Meta.sqla_session.add(inst)  # add inst to server
            schm.Meta.sqla_session.commit()  # commit to server
        except IntegrityError as err:
            schm.Meta.sqla_session.rollback()  # uncommit ! It doesn't works ! :-(
            response.status = HTTP_400
            return "IntegrityError ! {}".format(err.args)
        except SQLAlchemyError as err:
            schm.Meta.sqla_session.rollback()  # uncommit ! It doesn't works ! :-(
            response.status = HTTP_400
            return "Sqlalchemy didn't like it {}".format(err.__class__)

        response.status = HTTP_201
        return schm.dump(inst).data

    post.__doc__ = "Allow to create a new {} ressource".format(model_name)

    hug.post(path_post)(post)

    # And do the same for PUT/PATCHs requests
    def put(response, **kwargs):
        # Find ress
        try:
            inst = schm.get_instance(kwargs)
        except SQLAlchemyError as err:
            schm.Meta.sqla_session.rollback()  # uncommit ! It doesn't works ! :-(
            inst = None

        if inst is None:
            response.status = HTTP_400
            return cant_find_ress(kwargs)

        # update ressource data
        old_data = schm.dump(inst).data
        old_data.update(kwargs)

        data, error = schm.load(old_data, instance=inst)  # set data in mem

        if error:
            response.status = HTTP_400
            return error

        try:
            schm.Meta.sqla_session.commit()  # commit to serv
        except SQLAlchemyError as err:
            schm.Meta.sqla_session.rollback()  # uncommit ! It doesn't works ! :-(
            response.status = HTTP_400
            return "Sqlalchemy didn't like it {}".format(err.args)

        return schm.dump(inst).data

    put.__doc__ = "Allow to modify a new {} ressource".format(model_name)

    hug.put(path_put)(put)
    hug.patch(path_put)(put)

@hug.get("/sensors/{id_sensors}/{id_malette}/within/{n}", version=1)
def within(id_malette, id_sensors, n: hug.types.number, response):
    """return all the sensors within {n} meters to sensors(id_sensors, id_malette)"""
    schm = schema.SensorsSchema()
    ids = {"id_malette": id_malette, "id_sensors": id_sensors}

    try:
        inst = schm.get_instance(ids)
    except SQLAlchemyError:
        schm.Meta.sqla_session.rollback()
        inst = None

    if not inst:
        response.status = HTTP_400
        return "Can't find sensors"

    geom = json.dumps(inst.gps_pos)

    try:
        insts = schm.Meta.sqla_session.query(models.Sensors).filter(
            func.ST_DWithin(
                func.ST_GeomFromGeoJSON(geom),
                models.Sensors.gps_pos,
                n)
        )
    except SQLAlchemyError:
        schm.Meta.sqla_session.rollback()
        insts = None

    return schm.dump(insts, many=True).data

models.create_all()

generate_accessors(schema.CampaignSchema())
generate_accessors(schema.PanoramaSchema())
generate_accessors(schema.SensorsSchema())
generate_accessors(schema.TileSchema())
generate_accessors(schema.LotSchema())
generate_accessors(schema.CpSchema())
generate_accessors(schema.TrackEdgeSchema())
