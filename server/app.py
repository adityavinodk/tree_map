from flask import Flask, request, Response, session
import pymongo as pym
import datetime
import json
import os
import jwt
import hashlib
import config
from pprint import pprint
from random import randint
from math import inf

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

# is the parameter that decides whether a new cluster is to be created or not
def parameter(centroids, coordinates):
    highest_intracluster = 0
    lowest_intercluster = inf

    for i in centroids:
        for j in centroids:
            if i != j and distance(i,j) < lowest_intercluster:
                lowest_intercluster = distance(i,j)
    
    for i in coordinates:
        if distance(i[1], centroids[i[0]]) > highest_intracluster:
            highest_intracluster = distance(i[1], centroids[i[0]])

    if highest_intracluster >= lowest_intercluster: # if highest intracluster dist > lowest intercluster dist, parameter is not satisfied
        return False
    else:
        return True

# returns distance between two coordinates
def distance(coord1, coord2):
    return ((coord1[0]-coord2[0])**2 + (coord1[1] - coord2[1])**2)**0.5

# main clustering function that drives the whole thing
def cluster_main(centroids, coordinates):
    old_centroids = centroids
    new_centroids, coordinates = kmeanscluster(centroids, coordinates)

    while True:
        while old_centroids == new_centroids: # Performs k-means clustering
            old_centroids = new_centroids
            new_centroids, coordinates = kmeanscluster(old_centroids, coordinates)
        
        coordinates = sorted(coordinates, key = lambda x:x[0])
        
        if not parameter(new_centroids, coordinates): # Splits a cluster if the parameter isn't satisfied
            old_centroids = new_centroids
            new_centroids, coordinates = splitcluster(old_centroids, coordinates)
        else:
            break

    return sorted(coordinates, key = lambda x:x[0])

# k-means clustering code
def kmeanscluster(centroids, coordinates):
    coordinates = update_coordinates(centroids, coordinates) # Update coordinate markers based on previously generated centroids
    new_centroids = generate_centroids(sorted(coordinates, key= lambda x:x[0])) # Generate new centroids
    return new_centroids, coordinates

# updates the cluster that each coordinate belongs to, when new centroids are generated
def update_coordinates(centroids, coordinates):
    for i in coordinates:
        min_dist = inf
        for j in range(0, len(centroids)):
            cur_dist = distance(i[1], centroids[j])
            
            if cur_dist < min_dist:
                min_dist = cur_dist
                i[0] = j
    
    return coordinates

# calculates new centroids when new clusters are created
def generate_centroids(coordinates):
    xcentroids = list()

    current_centroid = coordinates[0][0] # holds current cluster number
    centroid = [0,0]
    count = 0
    for i in coordinates:
        if i[0] == current_centroid: # if i belongs to current cluster
            centroid[0] += i[1][0]
            centroid[1] += i[1][1]
            count += 1
        else: # for next cluster,
            centroid[0] /= count 
            centroid[1] /= count
            xcentroids.append(centroid.copy()) # append prev cluster centroid
            current_centroid = i[0] # update value of current cluster number
            count = 1
            centroid[0] = i[1][0]
            centroid[1] = i[1][1]
    centroid[0] /= count
    centroid[1] /= count
    xcentroids.append(centroid.copy()) # append last cluster centroid
    return xcentroids

# creates a new centroid using the point which is the furthest from the centroid of it's own cluster
def splitcluster(centroids, coordinates):
    max_dist = 0
    new_centroid = list()

    for i in coordinates:
        if distance(i[1], centroids[i[0]]) > max_dist:
            max_dist = distance(i[1], centroids[i[0]])
            new_centroid = i[1]

    centroids.append(new_centroid)
    coordinates = update_coordinates(centroids, coordinates)
    return centroids, coordinates


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
@app.route('/tree/clusters', methods=['GET'])
def create_clusters():
    coordstrs = db.trees.find({}) # returns a list of dictionaries
    coords = list()

    for i in coordstrs:
        loc = i['location']
        coords.append([0, loc])

    centroids = [coords[0][1], coords[1][1]] # needs to be updated, because currently i'm taking centroids as just the first two points of the whole set of coordinates
    final_coords = cluster_main(centroids, coords)

    message = 'Clusters created'
    
    for i in final_coords:
        print(i)
    success = True
    return Response(json.dumps({'message': message, 'success': success}), status=200, mimetype='application/json')
    
# returns the new clusters

# Endpoint to get nearest clusters based on the location
# @app.route('/tree/getNearestCluster', methods=['GET'])
# def get_nearest_cluster():
# Body contains address of location, return nearest cluster

if __name__ == "__main__":
    app.run(debug=True, port=8000, host='0.0.0.0')
