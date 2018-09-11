from src.dbLayer.dbClasses.categoryClasses import Category
from uuid import uuid4
import datetime

# from mongoengine import connect
# from src.dbLayer.dbConfig.config import MONGOIP, MONGOPORT, DBNAME
#
#
# connect(db=DBNAME, host=MONGOIP, port=MONGOPORT)


def read_category(**kwargs):
    """
    Helper function to fetch category objects as per **kwargs.
    :param kwargs: fields in the Category object
    :return: list of Category objects
    """
    # t = {'level':'level1'}
    print(kwargs)
    c = Category.objects(**kwargs).exclude('id')
    result = [ob.to_mongo().to_dict() for ob in c]
    return result


def write_category(**kwargs):
    c = Category(**kwargs)
    c.catId = str(uuid4())
    c.timestamp = datetime.datetime.now()
    c.save()


# print(read_category())