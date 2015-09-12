from flask import Flask, jsonify, abort, make_response, request
from pymongo import MongoClient
from bson import json_util
from bson.objectid import ObjectId
from flask.ext.httpauth import HTTPBasicAuth
from auth import authorized
from SummitServer import app
from secrets import mongo_db_connection_string

auth = HTTPBasicAuth()
print "connecting to MongoDB: " + mongo_db_connection_string
client = MongoClient( mongo_db_connection_string )
db = client['MongoLab-c']
if not db['activities']:
    db.create_collection('activities')
if not db['users']:
    db.create_collection('users')
if not db['mountains']:
    db.create_collection('mountains')

@auth.get_password
def get_password(username):
    if username is None:
        return None
    user = db['users'].find_one({'username' : username})
    if user is None:
        return None
    return user['password']

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

# Mountains api

@app.route('/api/v1.0/mountains', methods=['GET'])
@authorized
@auth.login_required
def get_mountains():
    mountains = db['mountains'].find().sort("name")
    mountains = {'mountains':mountains}
    return json_util.dumps(mountains)

@app.route('/api/v1.0/mountains/<string:mountain_id>', methods=['GET'])
@auth.login_required
@authorized
def get_mountain(mountain_id):
    mountain = db['mountains'].find_one({'_id' : mountain_id})
    if (mountain is None) or len(mountain) == 0:
        abort(404)
    return json_util.dumps(mountain)

@app.route('/api/v1.0/mountains/<string:mountain_id>/activities', methods=['GET'])
@auth.login_required
@authorized
def get_activity_from_mountain(mountain_id):
    query = {}
    query['mountain_id'] = mountain_id
    activities = db['activities'].find(query)
    activities = {'activities':activities}
    return json_util.dumps(activities)

# Activities API

@app.route('/api/v1.0/activities', methods=['POST'])
@auth.login_required
@authorized
def create_activity():
    if not request.json or not 'mountain_id' in request.json or not 'user_id' in request.json:
        abort(400)
    db['activities'].insert(request.json)
    return make_response(jsonify({'OK': 'Activity created'}), 201)

@app.route('/api/v1.0/activities', methods=['GET'])
@auth.login_required
@authorized
def get_activity():
    query = {}
    if 'user_id' in request.args:
        query['user_id'] = request.args.get('user_id')
    if 'mountain_id' in request.args:
        query['mountain_id'] = request.args.get('mountain_id')
    activities = db['activities'].find(query)
    activities = {'activities':activities}
    return json_util.dumps(activities)

# Users API

@app.route('/api/v1.0/users', methods=['POST'])
@authorized
def create_user():
    if not request.json or not 'username' in request.json or not 'password' in request.json:
        abort(400)
    request.json['_id'] = request.json['username']
    user_id = db['users'].insert(request.json)
    return make_response(jsonify({'OK': 'user created'}), 201)

@app.route('/api/v1.0/users/<user_id>/activities', methods=['GET'])
@auth.login_required
@authorized
def get_activity_from_user(user_id):
    query = {}
    query['user_id'] = user_id
    activities = db['activities'].find(query)
    activities = {'activities':activities}
    return json_util.dumps(activities)

@app.route('/api/v1.0/users/login', methods=['GET'])
@auth.login_required
@authorized
def check_user():
    """ Endpoint for app to check if password
    is correct for logins
    """
    user = db['users'].find_one({'username': auth.username()})
    return json_util.dumps(user)
