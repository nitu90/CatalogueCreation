from src.apiLayer.config import config
from src.dbLayer.dbHelper.categoryHelper import read_category, write_category, get_models
from src.dbLayer.dbConfig.config import MONGOIP, MONGOPORT, DBNAME
from flask import Flask, jsonify, request
from mongoengine import connect
from flasgger import Swagger
from flasgger.utils import swag_from


app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'Product Category Prediction',
    'uiversion': 2
}

Swagger(app)
connect(db=DBNAME, host=MONGOIP, port=MONGOPORT)

firstcry_models = get_models()


def generate_error_message(message, error_code):
    if error_code >= 500:
        return jsonify({'error_message': 'Internal Error : {}'.format(message)}), error_code
    else:
        return jsonify({'error_message': 'Bad request : Check input {}'.format(message)}), error_code


@app.route('/cw/categoryApis/getCategory', methods=['GET'])
@swag_from('/src/apiLayer/apiDocs/getCategory.yml')
def get_category():
    try:
        params = request.args.to_dict()
        invalid_params = [x for x in params.keys() if x not in config['valid_category_params']['get']]
        if invalid_params:
            return generate_error_message(message='params', error_code=404)
        params = {k: v for k, v in params.items() if v}
        try:
            return jsonify({'result': read_category(**params)}), 200
        except Exception as e:
            return generate_error_message(message='input required fields', error_code=400)
    except Exception as e:
        return generate_error_message(message=repr(e), error_code=500)


@app.route('/cw/categoryApis/createCategory', methods=['POST'])
@swag_from('/src/apiLayer/apiDocs/createCategory.yml')
def create_category():
    try:
        req = request.get_json()
        invalid_params = [x for x in req.keys() if x not in config['valid_category_params']['post']]
        if invalid_params:
            return generate_error_message(message='keys in request body', error_code=404)
        req = {k: v for k, v in req.items() if v}
        try:
            write_category(**req)
        except Exception as e:
            return generate_error_message(message='keys :'+repr(e), error_code=400)
        return jsonify({'message': 'Category created successfully'}), 201
    except Exception as e:
        return generate_error_message(message=repr(e), error_code=500)


@app.route('/cw/categoryApis/predict', methods=['POST'])
@swag_from('/src/apiLayer/apiDocs/predict.yml')
def predict_category():
    try:
        skus = request.get_json()['skus']
        if skus and isinstance(skus, list):
            req = request.args.get('level')
            if req and isinstance(req, str):
                if req.lower().strip() in config['valid_levels']:
                    level = req.lower().strip()
                    result = {level: list(firstcry_models[level].predict(skus))}
                    return jsonify({'result': [result]}), 200
                else:
                    return generate_error_message(message='level, no such level found', error_code=404)
            else:
                return jsonify({'result': list(map(lambda x: {x: list(firstcry_models[x].predict(skus))},
                                                   firstcry_models.keys()))}), 200
        else:
            return jsonify({'result': list()}), 200
    except Exception as e:
        return generate_error_message(message=repr(e), error_code=500)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555, debug=True)
