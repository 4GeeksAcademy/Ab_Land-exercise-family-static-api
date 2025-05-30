"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from utils import APIException, generate_sitemap
from datastructures import FamilyStructure
# from models import Person


app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

# Create the jackson family object
jackson_family = FamilyStructure("Jackson")


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


# Generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/members', methods=['GET'])
def handle_hello():
    # This is how you can use the Family datastructure by calling its methods
    members = jackson_family.get_all_members()
    response_body = members
    return jsonify(response_body), 200


@app.route('/members', methods=['POST'])
def add_new_member():
    body = request.get_json(silent=True)

    # Basic validation
    if body is None:
        return jsonify({'msg': 'Request body is missing'}), 400

    required_fields = ['first_name', 'age', 'lucky_numbers']
    for field in required_fields:
        if field not in body:
            return jsonify({'msg': f"Missing required field: {field}"}), 400

    # lucky_numbers to be a list
    lucky_numbers = body['lucky_numbers']
    if isinstance(lucky_numbers, int):
        lucky_numbers = [lucky_numbers]
    elif not isinstance(lucky_numbers, list):
        return jsonify({'msg': 'lucky_numbers must be a list or int'}), 400
    # gen id if not given
    id = ''
    if 'id' in body:
        id = body['id']
    else:
        id = jackson_family._generate_id()

    new_member = {
        'id': id,
        'first_name': body['first_name'],
        'last_name': jackson_family.last_name,
        'age': body['age'],
        'lucky_numbers': lucky_numbers
    }

    jackson_family.add_member(new_member)
    return jsonify(new_member), 200


@app.route('/members/<int:member_id>', methods=['GET'])
def get_member(member_id):
    member = jackson_family.get_member(member_id)
    if member:
        return jsonify(member), 200
    return jsonify({'msg': 'Member not found'}), 404


@app.route('/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    deleted = jackson_family.delete_member(member_id)
    if deleted:
        return jsonify({'msg': 'Member deleted successfully', 'done': deleted}), 200
    return jsonify({'msg': 'Member not found'}), 404


# This only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
