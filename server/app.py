from flask import Flask, request, Response, session, render_template
from flask_cors import CORS
import pymongo as pym
import json
import os
import hashlib
import config
from middleware.clusters import clusterMain, getNearestCluster
from middleware.authentication import authenticateUser, verifyUser, userDetails

if 'secret.key' not in os.listdir():
    print('Secret Key file missing. Check README.md for details')
    exit()
with open('secret.key', 'rb') as f:
    key = f.read()

app = Flask(__name__)
CORS(app)
app.config.from_object(config.Config)
app.secret_key = config.Config.SECRET_KEY

try:
    my_client = pym.MongoClient(app.config['MONGO_URL'], serverSelectionTimeoutMS=app.config['SERVER_SELECT_TIMEOUT'])
    print(my_client.server_info())
    print('\n----------------------------------------------------------------\nMongo connected. Starting app...\n----------------------------------------------------------------')
    db = my_client['Trees']
except pym.errors.ServerSelectionTimeoutError as err:
    print(err)
    print('\n----------------------------------------------------------------\nMongo not connected. Exiting app...\n----------------------------------------------------------------')
    exit()

# Serve React App
@app.route('/')
def my_index():
    return render_template("index.html")

# Endpoint to signup user
@app.route('/api/users/signup', methods=['POST'])
def signup():
    if request.method=='OPTIONS':
        return Response({'message': "200 OK"}, status=200, mimetype='application/json')
    else:
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
                    'password': hashed_password, 'location': req_data['location'], 'planted_trees': []}
            added_user = db.users.insert_one(data)
            token = authenticateUser(db, data['username'], data['password'], key)
            message = 'User successfully added'
            success = True
            return Response(json.dumps({'message': message, 'success': success, 'token': token, 'user_id': str(added_user.inserted_id)}), status=200, mimetype='application/json')

# Endpoint to login user
@app.route('/api/users/login', methods=['POST'])
def login():
    if request.method=='OPTIONS':
        return Response({'message': "200 OK"}, status=200, mimetype='application/json')
    else:
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
                token = authenticateUser(db, req_data['username'], hashed_password, key)
                message = 'Logged in successfully'
                success = True
                return Response(json.dumps({'message': message, 'success': success, 'token': token, 'user_id': str(user_found['_id'])}), status=200, mimetype='application/json')
            else:
                message = 'Error: Invalid Credentials'
                success = False
                return Response(json.dumps({'message': message, 'success': success}), status=400, mimetype='application/json')

# Endpoint to logout user
@app.route('/api/users/logout', methods=['POST'])
def logout():
    if request.method=='OPTIONS':
        return Response({'message': "200 OK"}, status=200, mimetype='application/json')
    else:
        if 'token' not in request.headers:
            message = 'Error: Missing header token'
            success = False
            return Response(json.dumps({'message': message, 'success': success}), status=400, mimetype='application/json')
        token = request.headers['token']
        verified = verifyUser(db, token, key)[0]
        if not verified:
            message = 'Error: Invalid token'
            success = False
            return Response(json.dumps({'message': message, 'success': success}), status=401, mimetype='application/json')
        db.usersessions.delete_one({'token': token})
        message = 'Logged out successfully'
        success = True
        return Response(json.dumps({'message': message, 'success': success}), status=200, mimetype='application/json')

# Endpoint to add tree at a particular location
@app.route('/api/tree/plant', methods=['POST'])
def addTree():
    if request.method=='OPTIONS':
        return Response({'message': "200 OK"}, status=200, mimetype='application/json')
    else:
        req_data = request.get_json()
        if 'token' not in request.headers:
            message = 'Error: Missing header token'
            success = False
            return Response(json.dumps({'message': message, 'success': success}), status=400, mimetype='application/json')
        token = request.headers['token']
        verified, payload = verifyUser(db, token, key)
        if not verified:
            message = 'Error: Invalid token'
            success = False
            return Response(json.dumps({'message': message, 'success': success}), status=401, mimetype='application/json')
        if 'location' not in req_data or len(req_data['location']) != 2:
            message = 'Error: Missing fields in request body'
            success = False
            return Response(json.dumps({'message': message, 'success': success}), status=400, mimetype='application/json')
        user = userDetails(db, payload)
        user_query = {'_id': user['id']}
        user_document = db.users.find_one(user_query)
        data = {'created_by': user['id'], 'location': req_data['location']}
        planted_tree = db.trees.insert_one(data)
        updated_planted_trees = {"$set":{"planted_trees": user_document['planted_trees'] + [planted_tree.inserted_id]}}
        db.users.update_one(user_query, updated_planted_trees)
        message = 'Tree added successfully at '+str(req_data['location'])
        success = True
        return Response(json.dumps({'message': message, 'success': success}), status=200, mimetype='application/json')

# Endpoint to get list of trees planted by a user
@app.route('/api/tree/getPlantedTrees', methods=['GET'])
def getPlantedTrees():
    if 'token' not in request.headers:
        message = 'Error: Missing header token'
        success = False
        return Response(json.dumps({'message': message, 'success': success}), status=400, mimetype='application/json')
    token = request.headers['token']
    verified, payload = verifyUser(db, token, key)
    if not verified:
        message = 'Error: Invalid token'
        success = False
        return Response(json.dumps({'message': message, 'success': success}), status=401, mimetype='application/json')
    user = userDetails(db, payload)
    user_query = {'_id': user['id']}
    user_document = db.users.find_one(user_query)
    tree_id_list = [str(x) for x in user_document['planted_trees']]
    message = 'Successfully retrieved trees planted by '+ user['username']
    success = True
    return Response(json.dumps({'message': message, 'success': success, 'planted_trees': tree_id_list}), status=200, mimetype='application/json')

# Endpoint to create clusters based on the trees locations
@app.route('/api/tree/clusters', methods=['GET'])
def create_clusters():
    tree_documents = db.trees.find({})  # returns a list of dictionaries
    coordinates = []
    for document in tree_documents:
        coordinates.append(
            {'id': document['_id'], 'location': document['location']})
    if len(coordinates) == 0:
        success = False
        message = 'No trees found.'
        return Response(json.dumps({'message': message, 'success': success}), status=204, mimetype='application/json')
    db.clusters.delete_many({})
    final_clusters = clusterMain(coordinates, iterations = 10)
    list_clusters = []
    db.clusters.insert_many([final_clusters[cluster]
                             for cluster in final_clusters])
    for cluster in final_clusters:
        cluster_object = final_clusters[cluster]
        list_clusters.append({'id': str(cluster_object['_id']), 'trees': [str(
            x) for x in cluster_object['trees']], 'centroid': cluster_object['centroid']})
    success = True
    message = 'Clusters created successfully'
    return Response(json.dumps({'message': message, 'success': success, 'clusters': list_clusters}), status=200, mimetype='application/json')

# Endpoint to get nearest clusters based on the location
@app.route('/api/tree/getNearestCluster', methods=['GET'])
def get_nearest_cluster():
    req_data = request.get_json()
    if 'token' not in request.headers:
        message = 'Error: Missing header token'
        success = False
        return Response(json.dumps({'message': message, 'success': success}), status=400, mimetype='application/json')
    token = request.headers['token']
    verified = verifyUser(db, token, key)[0]
    if not verified:
        message = 'Error: Invalid token'
        success = False
        return Response(json.dumps({'message': message, 'success': success}), status=401, mimetype='application/json')
    if 'location' not in req_data or len(req_data['location']) != 2:
        message = 'Error: Missing fields in request body'
        success = False
        return Response(json.dumps({'message': message, 'success': success}), status=400, mimetype='application/json')
    clusters = db.clusters.find({})
    clusters_dict = {}
    for cluster in clusters:
        clusters_dict[str(cluster['_id'])] = {
            'centroid': cluster['centroid'], 'trees': [str(x) for x in cluster['trees']]}
    if len(clusters_dict) == 0:
        success = False
        message = 'No clusters found.'
        return Response(json.dumps({'message': message, 'success': success}), status=204, mimetype='application/json')
    nearest_cluster_id = getNearestCluster(clusters_dict, req_data['location'])
    nearest_cluster = {'id': nearest_cluster_id,
                       'centroid': clusters_dict[nearest_cluster_id]['centroid'], 'trees': clusters_dict[nearest_cluster_id]['trees']}
    success = True
    message = 'Nearest Cluster succesffully found'
    return Response(json.dumps({'message': message, 'success': success, 'nearest_cluster': nearest_cluster}), status=200, mimetype='application/json')

if __name__ == "__main__":
    app.run(debug=True, port=8000, host='0.0.0.0')
