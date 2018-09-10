from mongoengine import connect
from src.dbLayer.dbClasses.categoryClasses import Category
from src.dbLayer.dbConfig.config import MONGOIP, MONGOPORT, DBNAME, CATEGORYCOLLECTIONNAME
import json


connect(db=DBNAME, host=MONGOIP, port=MONGOPORT)


def read_category(**kwargs):
    """
    Helper function to fetch category objects as per **kwargs.
    :param kwargs: fields in the Category object
    :return: list of Category objects
    """
    t = {'usedForModel': True, 'catId__contains': '432'}

    c = Category.objects(t)
    d = {'result': [ob.to_mongo().to_dict() for ob in c]}
    print(d)
    # for cat in c:
    #     print(cat.to_mongo().to_dict())

    # print(type(c))
    # print(c)

read_category()