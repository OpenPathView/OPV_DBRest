from math import ceil
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields, decorators, ValidationError
import json

from dbrest.models import (
                          Campaign,
                          Cp, Lot,
                          Panorama,
                          Sensors,
                          Tile,
                          TrackEdge,
                          session
                          )

__all__ = ['CampaignSchema', 'CpSchema', 'LotSchema', 'SensorsSchema', 'TileSchema']

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
