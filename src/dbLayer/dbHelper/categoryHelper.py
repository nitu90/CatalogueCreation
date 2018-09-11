from src.dbLayer.dbClasses.categoryClasses import Category
from src.apiLayer.config import config
from uuid import uuid4
import datetime
import dill
import numpy as np

# from mongoengine import connect
# from src.dbLayer.dbConfig.config import MONGOIP, MONGOPORT, DBNAME
#
#
# connect(db=DBNAME, host=MONGOIP, port=MONGOPORT)


def read_category(**kwargs):
    """
    Helper function to fetch category objects as per **kwargs.
    :param kwargs: fields in the Category object. Refer '/src/apiLayer/apiDocs/getCategory.yml'
    :return: list of Category objects
    """
    # t = {'level':'level1'}
    print(kwargs)
    c = Category.objects(**kwargs).exclude('id')
    result = [ob.to_mongo().to_dict() for ob in c]
    return result


def write_category(**kwargs):
    """
    Helper function to write a new category to db
    :param kwargs: attributes of the category to be created. Refer '/src/apiLayer/apiDocs/createCategory.yml'
    :return: None
    """
    c = Category(**kwargs)
    c.catId = str(uuid4())
    c.timestamp = datetime.datetime.now()
    c.save()


class Model:
    """
    Helper class to load a model.
    """
    def __init__(self, dir_path):
        """
        Loads the vectorizer, scaler and classifier given a directory path which points to a folder containing
        these pickle files
        :param dir_path: <str>, directory path
        """
        self.vectorizer = dill.load(open(dir_path+"/vectorizer.pkl", "rb"))
        self.scaler = dill.load(open(dir_path+"/scaler.pkl", "rb"))
        self.classifier = dill.load(open(dir_path+"/classifier.pkl", "rb"))

    def predict(self, list_of_titles):
        """
        Predict the categories given a list of skus
        :param list_of_titles: <list>, List of Skus
        :return: <list>, ordered list of categories corresponding to *list_of_titles*
        """
        sentence_vectors = self.vectorizer.transform(list_of_titles)
        scaled_vectors = self.scaler.transform(sentence_vectors)
        predictions = self.classifier.predict(scaled_vectors)
        return predictions


def get_models():
    """
    Helper function to load all the models at different category levels
    :param model_paths: <dict>, model paths at different levels. Same as '/apiLayer/config > model_paths'
    :return: <dict>,
                    {
                        'level1' : Model Object,
                        'level2' : Model Object
                    }
    """
    models = dict()
    for level in config['valid_levels']:
        models[level] = Model(config['model_paths'][level])
    return models
