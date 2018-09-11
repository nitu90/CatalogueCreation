from mongoengine import *
from src.dbLayer.dbConfig.config import CATEGORYCOLLECTIONNAME


class Category(Document):
    meta = {
        'collection': CATEGORYCOLLECTIONNAME
    }
    catId = StringField(required=True, unique=True)
    name = StringField(required=True, unique=True)
    parentId = ListField(StringField(), required=True)
    alias = ListField(StringField())
    timestamp = DateTimeField(required=True)
    creatorType = StringField(required=True, choices=['auto', 'manual'])
    creatorName = StringField(default='auto', choices=['US', 'KS', 'DS', 'LP', 'NK', 'auto'])
    usedForModel = IntField(default=5, choices=[5, 1])
    level = StringField(required=True, choices=['level1', 'level2', 'level3'])
    comments = StringField()
