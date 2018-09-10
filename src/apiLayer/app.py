from flask import Flask, jsonify, request
# from config import config, feedbackPath
# from custom_classes import Model, generate_error_message
# import numpy as np
# import pandas as pd
# import datetime
from flasgger import Swagger

app = Flask(__name__)
Swagger(app)

# firstcry_models = {
#     'level1': Model(config['firstcry']['level1'])
# }
#
#
# @app.route('/cw/getCategories', methods=['GET'])
# def get_classes():
#     try:
#         level = request.args.get('level')
#         if level and isinstance(level, str):
#             lvl = level.lower().strip()
#             if lvl in firstcry_models.keys():
#                 return jsonify({'result': [{lvl: list(firstcry_models[lvl].classifier.classes_)}]}), 200
#             else:
#                 return jsonify({'error_message': 'Bad Input, no such level found'}), 404
#         else:
#             return jsonify({'result': list(map(lambda x: {x: list(firstcry_models[x].classifier.classes_)},
#                                                firstcry_models.keys()))}), 200
#     except Exception as e:
#         return jsonify({'error_message': "Internal error : {}".format(repr(e))}), 500
#
#
#
# @app.route('/cw/predict', methods=['POST'])
# def predict_fmcd():
#     try:
#         skus = request.get_json()['skus']
#         if skus and isinstance(skus, list):
#             req = request.args.get('level')
#             if req and isinstance(req, str):
#                 if req.lower().strip() in firstcry_models.keys():
#                     level = req.lower().strip()
#                     result = {level: list(firstcry_models[level].predict(skus))}
#                     return jsonify({'result': [result]}), 200
#                 else:
#                     return jsonify({'error_message': 'Bad Input, no such level found'}), 404
#             else:
#                 return jsonify({'result': list(map(lambda x: {x: list(firstcry_models[x].predict(skus))},
#                                                    firstcry_models.keys()))}), 200
#         else:
#             return jsonify({'result': list()}), 200
#     except Exception as e:
#         return jsonify({'error_message': 'Internal error : {}'.format(repr(e))}), 500
#
#
#
# @app.route('/categoryId/feedback/labelSku', methods=['GET', 'POST'])
# def write_feedback():
#     try:
#         if request.method == 'GET':
#             return jsonify({
#                 'user': '<userName>',
#                 'segment': '<segmentName>',
#                 'level': '<level1/level2/...>',
#                 'sku': '<title>',
#                 'response': {
#                     'modelContainsCorrectClass': '<True/False>',
#                     'correctClass': '<correctClassLabel>',
#                     'clustrId': '<Clustr permanent categoryId if \'modelContainsCorrectClass\' = False>'
#                 },
#                 'comments': '<any comments/ insights>'
#             }), 200
#         else:
#             req = request.get_json()
#             if all(key in req for key in ['segment', 'user', 'sku', 'level', 'response']):
#                 if all(key in req['response'] for key in ['modelContainsCorrectClass', 'correctClass', 'clustrId']):
#                     if req['response']['modelContainsCorrectClass'] is False and not req['response']['clustrId']:
#                         return jsonify(
#                             {'error_message': 'ClustrId is mandatory if \'modelContainsCorrectClass\'=False'}), 400
#                     else:
#                         req['timestamp'] = str(datetime.datetime.now())
#                         record = pd.io.json.json_normalize(req)
#                         with open(feedbackPath+'/feedback.csv', 'a') as fp:
#                             record.to_csv(fp, header=False, encoding='utf-8')
#                             fp.close()
#                         return jsonify(
#                             {'message': 'Feedback for sku {} has been submitted'.format(req['sku'])}), 201
#                 else:
#                     return jsonify({'error_message': 'bad input'}), 400
#             else:
#                 return jsonify({'error_message': 'bad input'}), 400
#
#     except Exception as e:
#         return jsonify({'error_message': "Internal error : {}".format(repr(e))}), 500
#
#
# @app.route('/categoryId/feedback/createCategory', methods=['GET', 'POST'])
#


@app.route('/cw/getCategories', methods=['GET'])
def get_categories():
    """
    This is an awesome API!!! Fetch one/more category(s) based on below mentioned params
    ---
    tags:
        - Category API
    parameters:
        -   name: categoryName
            in: path
            type: string
            required: false
            description: Fetch category(s) by name
        -   name: level
            in: path
            type: string
            required: false
            description: Fetch category(s) at a given level
        -   name: parentId
            in: path
            type: string
            required: false
            description: Fetch category(s) by parent's Id
        -   name: id
            in: path
            type: string
            required: false
            description: Fetch category by id
        -   name: usedForModel
            in: path
            type: boolean
            required: false
            description: If True, returns only those categories which are used for modelling. If False, returns others.
        -   name: creatorType
            in: path
            type: string
            required: false
            enum: ['auto','manual']
            description: Fetch category(s) by creatorType, ie. manual vs auto(from websites)
        -   name: creatorName
            in: path
            type: string
            required: false
            description: Fetch category(s) by person who created it
    """
    params = request.args.keys()
    wrong_param = [x for x in params if x not in cat_df.columns]
    if wrong_param:
        return get_error_message(message='params', error_code=404)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555, debug=True)

