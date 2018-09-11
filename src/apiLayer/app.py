from flask import Flask, jsonify, request
from mongoengine import connect
from flasgger import Swagger
from flasgger.utils import swag_from
from src.apiLayer.config import valid_category_params
from src.dbLayer.dbHelper.categoryHelper import read_category, write_category
from src.dbLayer.dbConfig.config import MONGOIP, MONGOPORT, DBNAME


app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'Product Category Prediction',
    'uiversion': 2
}
Swagger(app)

connect(db=DBNAME, host=MONGOIP, port=MONGOPORT)


def generate_error_message(message, error_code):
    if error_code >= 500:
        return jsonify({'error_message': 'Internal Error : {}'.format(message)}), error_code
    else:
        return jsonify({'error_message': 'Bad request : Check input {}'.format(message)}), error_code


@app.route('/cw/getCategory', methods=['GET'])
@swag_from('/src/apiLayer/apiDocs/getCategory.yml')
def get_category():
    try:
        params = request.args.to_dict()
        invalid_params = [x for x in params.keys() if x not in valid_category_params['get']]
        if invalid_params:
            return generate_error_message(message='params', error_code=404)
        params = {k: v for k, v in params.items() if v}
        return jsonify({'result': read_category(**params)}), 200
    except ValidationError as e:
        return generate_error_message(message='input required fields', error_code=400)
    except Exception as e:
        return generate_error_message(message=repr(e), error_code=500)


@app.route('/cw/createCategory', methods=['POST'])
@swag_from('/src/apiLayer/apiDocs/createCategory.yml')
def create_category():
    try:
        req = request.get_json()
        invalid_params = [x for x in req.keys() if x not in valid_category_params['post']]
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555, debug=True)
