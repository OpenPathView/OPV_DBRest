from math import ceil
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields, decorators, ValidationError
import json

from dbrest.models import Campaign, Cp, Lot, Panorama, Sensors, Tile, TrackEdge, Reconstruction, Shot, Path, PathNode, PathDetails, PathEdge, Virtualtour, VirtualtourPath, VirtualtourHihlight
from dbrest.db import session

__all__ = ['CampaignSchema', 'CpSchema', 'LotSchema', 'LotWithSensorsSchema',
           'SensorsSchema', 'TileSchema', 'TrackEdgeSchema',
           'ReconstructionSchema', 'ShotSchema', 'PathSchema',
           'PathNodeSchema', 'PathDetailsSchema', 'PathEdgeSchema',
           'VirtualtourSchema', 'VirtualtourPathSchema', 'VirtualtourHihlightSchema']

class BaseSchema(ModelSchema):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page = 0
        self.page_size = 0
        self.page_count = 0

    def filter_instances(self, data):
        """Retrieve existing records by key(s).
        greatly inspired by get_instance of ModelSchema"""

        try:
            self.page_size = int(data.get('page[size]', 0))
            self.page = int(data.get('page', 0))
        except ValueError:
            self.page_size = 0
            self.page = 0

        mapper = self.opts.model.__mapper__
        props = mapper.columns.keys()  # get all props of model

        filters = {  # create filter list
            prop: data.get(prop)
            for prop in props
            if data.get(prop) is not None
        }

        query = self.session.query(self.opts.model).filter_by(**filters)

        if self.page_size:
            self.page_count = ceil(query.count() / self.page_size) - 1  # 0-indexing
            query = query.limit(self.page_size)
            query = query.offset(self.page_size * self.page)

        return query

    @decorators.post_dump(pass_many=True)
    def wrap_with_pagination(self, data, many):
        """Return just"""
        if not many:  # has pagination ?
            return data

        ret = {
            "page": self.page,  # current page
            "total": self.page_count,  # total count of pages
            "page_size": self.page_size,  # nbr of ress by page
            "objects": data  # datas
        }
        return ret

    class Meta:
        sqla_session = session

class GeoJSON(fields.Field):
    def _deserialize(self, value, attr, data):
        try:
            return json.dumps(value)
        except json.JSONDecodeError:
            ValidationError('Not a valid GeoJSON', attr)

class CampaignSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Campaign

class CpSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Cp

class LotSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Lot

class LotWithSensorsSchema(BaseSchema):
    sensors = fields.Nested('SensorsSchema')
    class Meta(BaseSchema.Meta):
        model = Lot

class PanoramaSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Panorama
class SensorsSchema(BaseSchema):
    gps_pos = GeoJSON()

    class Meta(BaseSchema.Meta):
        model = Sensors

class TileSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Tile

class TrackEdgeSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = TrackEdge

class ReconstructionSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Reconstruction

class ShotSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Shot

class PathSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Path

# ---- Virtual tour roads/paths ----
class PathNodeSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = PathNode


class PathDetailsSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = PathDetails


class PathEdgeSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = PathEdge


# ---- Virtual tours, final render data for viewer/embed ----
class VirtualtourSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Virtualtour


class VirtualtourPathSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = VirtualtourPath


class VirtualtourHihlightSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = VirtualtourHihlight

