from flask import Flask, request, Response, session
import pymongo as pym
import datetime
import json
import os
import jwt
import hashlib
import config

if 'secret.key' not in os.listdir():
    print('Secret Key file missing. Check README.md for details')
    exit()
with open('secret.key', 'rb') as f:
    key = f.read()

app = Flask(__name__)
app.config.from_object(config.Config)
app.secret_key = config.Config.SECRET_KEY

my_client = pym.MongoClient(app.config['MONGO_URL'])
db = my_client['Trees']

# returns token for authentication, adds token to usersession
def authenticate_user(username, password):
    payload = {'username': username, 'password': password,
               'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)}
    token = jwt.encode(payload, key, algorithm='HS256').decode('utf-8')
    db.usersessions.insert_one({'token': token})
    return token

# validates the token provided by user
def verify_user(token):
    verified = False
    try:
        payload = jwt.decode(token, key, algorithm='HS256')
        if db.usersessions.find_one({'token': token}) != None:
            verified = True
    except jwt.exceptions.InvalidSignatureError:
        verified = False
    except jwt.ExpiredSignatureError:
        verified = False
        if db.usersessions.find_one({'token': token}) != None:
            db.usersessions.delete_one({'token': token})
    return verified, payload

# returns the user details after token is verified
def user_details(payload):
    user_details = {}
    user = db.users.find_one({'username': payload['username']})
    if user != None:
        user_details = {'username': user['username'],
                        'id': user['_id'], 'location': user['location']}
    return user_details

# Endpoint to signup user
@app.route('/users/signup', methods=['POST'])
def signup():
    req_data = request.get_json()
    if 'username' not in req_data or 'password' not in req_data or 'location' not in req_data or len(req_data['location']) != 2:
        message = 'Error: Missing fields in request body'
        success = False
        return Response(json.dumps({'message': message, 'success': success}), status=400, mimetype='application/json')
    if db.users.find_one({'username': req_data['username']}) != None:
        message = 'Error: User already exists'
        success = False
        return Response(json.dumps({'message': message, 'success': success}), status=409, mimetype='application/json')
    else:
        hashed_password = hashlib.sha1(
            req_data['password'].encode()).hexdigest()
        data = {'username': req_data['username'],
                'password': hashed_password, 'location': req_data['location']}
        db.users.insert_one(data)
        token = authenticate_user(data['username'], data['password'])
        message = 'User successfully added'
        success = True
        return Response(json.dumps({'message': message, 'success': success, 'token': token}), status=200, mimetype='application/json')

# Endpoint to login user
@app.route('/users/login', methods=['POST'])
def login():
    req_data = request.get_json()
    if 'username' not in req_data or 'password' not in req_data:
        message = 'Error: Missing fields in request body'
        success = False
        return Response(json.dumps({'message': message, 'success': success}), status=400, mimetype='application/json')
    user_found = db.users.find_one({'username': req_data['username']})
    if user_found == None:
        message = 'Error: User not found'
        success = False
        return Response(json.dumps({'message': message, 'success': success}), status=404, mimetype='application/json')
    else:
        hashed_password = hashlib.sha1(
            req_data['password'].encode()).hexdigest()
        if user_found['password'] == hashed_password:
            token = authenticate_user(req_data['username'], hashed_password)
            message = 'Logged in successfully'
            success = True
            return Response(json.dumps({'message': message, 'success': success, 'token': token}), status=200, mimetype='application/json')
        else:
            message = 'Error: Invalid Credentials'
            success = False
            return Response(json.dumps({'message': message, 'success': success}), status=400, mimetype='application/json')

# Endpoint to logout user
@app.route('/users/logout', methods=['POST'])
def logout():
    if 'token' in request.headers:
        token = request.headers['token']
    else:
        message = 'Error: Missing header token'
        success = False
        return Response(json.dumps({'message': message, 'success': success}), status=400, mimetype='application/json')
    verified, payload = verify_user(token)
    if not verified:
        message = 'Error: Invalid token'
        success = False
        return Response(json.dumps({'message': message, 'success': success}), status=401, mimetype='application/json')
    db.usersessions.delete_one({'token': token})
    message = 'Logged out successfully'
    success = True
    return Response(json.dumps({'message': message, 'success': success}), status=200, mimetype='application/json')

# Endpoint to add tree at a particular location
@app.route('/tree/add', methods=['POST'])
def add_tree():
    req_data = request.get_json()
    if 'token' not in request.headers:
        message = 'Error: Missing header token'
        success = False
        return Response(json.dumps({'message': message, 'success': success}), status=400, mimetype='application/json')
    if 'location' not in req_data or len(req_data['location']) != 2:
        message = 'Error: Missing fields in request body'
        success = False
        return Response(json.dumps({'message': message, 'success': success}), status=400, mimetype='application/json')
    token = request.headers['token']
    verified, payload = verify_user(token)
    user = user_details(payload)
    if not verified:
        message = 'Error: Invalid token'
        success = False
        return Response(json.dumps({'message': message, 'success': success}), status=401, mimetype='application/json')
    data = {'created_by': user['id'], 'location': req_data['location']}
    db.trees.insert_one(data)
    message = 'Tree added successfully at '+str(req_data['location'])
    success = True
    return Response(json.dumps({'message': message, 'success': success}), status=200, mimetype='application/json')

# Endpoint to create clusters based on the trees locations
# @app.route('/tree/clusters', methods=['GET'])
# def create_clusters():
# returns the new clusters

# Endpoint to get nearest clusters based on the location
# @app.route('/tree/getNearestCluster', methods=['GET'])
# def get_nearest_cluster
# Body contains address of location, return nearest cluster

if __name__ == "__main__":
    app.run(debug=True, port=8000, host='0.0.0.0')
