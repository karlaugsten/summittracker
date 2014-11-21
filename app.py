from flask import Flask, jsonify, abort, make_response, request
from pymongo import MongoClient
from bson import json_util
from bson.objectid import ObjectId
from flask.ext.httpauth import HTTPBasicAuth
from auth import authorized

auth = HTTPBasicAuth()

client = MongoClient('mongodb://summittrackerdb.cloudapp.net:27017/')
db = client['summittracker']

app = Flask(__name__)

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

@app.route('/api/v1.0/mountains', methods=['GET'])
@authorized
@auth.login_required
def get_mountains():
    mountains = db['mountains'].find()
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

# Activities API

@app.route('/api/v1.0/activity', methods=['POST'])
@auth.login_required
@authorized
def create_activity():
    if not request.json or not 'mountain_id' in request.json or not 'user_id' in request.json:
        abort(400)
    db['activities'].insert(request.json)
    return make_response(jsonify({'OK': 'Activity created'}), 201)

@app.route('/api/v1.0/activity', methods=['GET'])
@auth.login_required
@authorized
def get_activity_from_user():
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
    user_id = db['users'].insert(request.json)
    return "you suck", 201

@app.route('/api/v1.0/users/login', methods=['GET'])
@auth.login_required
@authorized
def check_user():
    """ Endpoint for app to check if password
    is correct for logins
    """
    user = db['users'].find_one({'username': auth.username()})
    return json_util.dumps(user)
    

if __name__ == '__main__':
    app.run(debug=True)