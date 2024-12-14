from flask import jsonify, request
from . import api
import datetime

@api.route('/test', methods=['GET'])
def test_route():
    return jsonify({
        "message": "Test route working helooo",
        "service": "API Routes Module",
        "timestamp": datetime.datetime.now().isoformat()
    }) 

@api.route('/custom', methods=['GET'])
def custom_route():
    return jsonify({
        "message": "hiiiiii",
        "service": "API Routes Module",
        "timestamp": datetime.datetime.now().isoformat()
    }) 

@api.route('/createuserentry', methods=['POST'])
def create_user_entry():
    data = request.get_json()
    field_value = data.get('entry')
    
    #if not data:
    #     return jsonify({"error": "No data provided"}), 400

    return jsonify({
        "message": "here is yr" + field_value,
        "service": "API Routes Module",
        "timestamp": datetime.datetime.now().isoformat()
    })

