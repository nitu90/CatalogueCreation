from mongoengine import *
from src.dbLayer.dbConfig.config import MONGOIP, MONGOPORT, DBNAME
from src.dbLayer.dbClasses.categoryClasses import Category
from uuid import uuid4
import datetime


connect(db=DBNAME, host=MONGOIP, port=MONGOPORT)


temp = Category(catId='1234',
                name=str(uuid4()),
                parentId=[str(uuid4()), str(uuid4())],
                timestamp=datetime.datetime.now(),
                creatorType='auto',
                level='level1')
temp.save()
