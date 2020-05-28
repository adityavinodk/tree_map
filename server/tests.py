import os
import unittest
import json
import random
import hashlib

from app import app

class BasicTests(unittest.TestCase):

    ############################
    #### setup and teardown ####
    ############################

    # executed prior to each test
    def setUp(self):
        self.coords = [random.randint(12845, 13033)/1000, random.randint(77461, 77689)/1000]

        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
        #     os.path.join(app.config['BASEDIR'], TEST_DB)
        self.app = app.test_client()
        with app.test_client() as client:
            # send data as POST form to endpoint
            requestData = {
                "username": "testuser",
                "password": ""
            }
            response = client.post(
                '/api/users/login',
                data=json.dumps(requestData),
                headers={"Content-Type": "application/json"}
            )
            data = json.loads(response.data)
            self.logintoken = data["token"]

    # executed after each test
    def tearDown(self):
        pass


    ###############
    #### tests ####
    ###############

    
    # TEST 1
    # Plant a tree without a token
    # API is a POST method needing a token and a location
    # Test sends only location
    # Expected response is 400
    def test_plant_without_token(self):
        with app.test_client() as client:
            # send data as POST form to endpoint
            requestData = {
                "location": self.coords
            }
            response = client.post(
                '/api/tree/plant',
                data=json.dumps(requestData),
                headers={"Content-Type": "application/json"}
            )
            self.assertEqual(
                response.status_code, 400
            )
    
    # TEST 2
    # Plant a tree without a location
    # API is a POST method needing a token and a location
    # Test sends only token
    # Expected response is 400
    def test_plant_without_location(self):
        with app.test_client() as client:
            # send data as POST form to endpoint
            response = client.post(
                '/api/tree/plant',
                headers={"Content-Type": "application/json", "token": self.logintoken}
            )
            self.assertEqual(
                response.status_code, 400
            )

     # TEST 3
     # Plant a tree with an invalid token
     # API is a POST method needing a token and a location
     # Test sends both, but the token is invalid
     # Expected response is 401
    def test_plant_invalid_token(self):
        with app.test_client() as client:
            # send data as POST form to endpoint
            requestData = {
                "location": self.coords
            }

            rand_string = "assassin"
            hashed_token = hashlib.sha1(rand_string.encode()).hexdigest()

            hashed_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6InVzZXIxIiwicGFzc3dvcmQiOiJhOTk5M2UzNjQ3MDY4MTZhYmEzZTI1NzE3ODUwYzI2YzljZDBkODlkIiwiZXhwIjoxNTkwNzM1NDc0fQ.ulV8GclaJL_uHWLuWeTaEiGfRylTYxrqCUXLrMmzUF8"

            response = client.post(
                '/api/tree/plant',
                data=json.dumps(requestData),
                headers={"Content-Type": "application/json", "token": hashed_token}
            )
            self.assertEqual(
                response.status_code, 401
            )
    
    # TEST 4
    # Plant a tree, proper
    # API is a POST method needing a token and a location
    # Test sends necessary data
    # Expected response is 200
    def test_plant(self):
        with app.test_client() as client:
            # send data as POST form to endpoint
            requestData = {
                "location": self.coords
            }
            response = client.post(
                '/api/tree/plant',
                data=json.dumps(requestData),
                headers={"Content-Type": "application/json", "token": self.logintoken}
            )
            self.assertEqual(
                response.status_code, 200
            )

    # TEST 5
    # Get all planted trees
    # API is a GET method needing a token
    # Test sends necessary data
    # Expected response is 200
    def test_get_planted_trees(self):
        with app.test_client() as client:
            # send data as GET to endpoint
            response = client.get(
                '/api/tree/getPlantedTrees',
                headers={"token": self.logintoken}
            )
            # data = json.loads(response.data)
            # trees = data["planted_trees"]
            # print(trees)
            self.assertEqual(
                response.status_code, 200
            )
    
    # TEST 6
    # Get all planted trees
    # API is a GET method needing a token
    # Test calls a POST on the route
    # Expected response is 405
    def test_get_planted_trees_with_post(self):
        with app.test_client() as client:
            # send data as POST to endpoint
            requestData = {
                "token":    self.logintoken
            }
            response = client.post(
                '/api/tree/getPlantedTrees',
                data=json.dumps(requestData),
                headers={"Content-Type": "application/json"}
            )
            self.assertEqual(
                response.status_code, 405
            )
    
    # TEST 7
    # Get all planted trees
    # API is a GET method needing a token
    # Test doesn't send a token
    # Expected response is 404
    def test_get_planted_trees_without_token(self):
        with app.test_client() as client:
            # send data as GET to endpoint
            response = client.get(
                '/api/tree/getPlantedTrees'
            )
            self.assertEqual(
                response.status_code, 400
            )
    
    # TEST 8
    # Get all planted trees
    # API is a GET method needing a token
    # Test doesn't send a valid token
    # Expected response is 401
    def test_get_planted_trees_invalid_token(self):
        with app.test_client() as client:
            requestData = {
                "token":    self.logintoken
            }

            rand_string = "assassin"
            hashed_token = hashlib.sha1(rand_string.encode()).hexdigest()

            hashed_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6InVzZXIxIiwicGFzc3dvcmQiOiJhOTk5M2UzNjQ3MDY4MTZhYmEzZTI1NzE3ODUwYzI2YzljZDBkODlkIiwiZXhwIjoxNTkwNzM1NDc0fQ.ulV8GclaJL_uHWLuWeTaEiGfRylTYxrqCUXLrMmzUF8"

            # send data as GET to endpoint
            response = client.get(
                '/api/tree/getPlantedTrees',
                data=json.dumps(requestData),
                headers={"Content-Type": "application/json", "token": hashed_token}
            )

            self.assertEqual(
                response.status_code, 401
            )
    
    # TEST 9
    # Get nearest cluster
    # API is a GET method needing a token and location
    # Test sends necessary data
    # Expected response is 200
    def test_get_nearest(self):
        with app.test_client() as client:
            requestData = {
                "location":    self.coords
            }
            # send data as GET to endpoint
            response = client.get(
                '/api/tree/getNearestCluster',
                data=json.dumps(requestData),
                headers={"Content-Type": "application/json", "token": self.logintoken}
            )
            self.assertTrue(
                response.status_code in [204, 200]
            )
    
    # TEST 10
    # Get nearest cluster
    # API is a GET method needing a token and location
    # Test doesn't send a valid token
    # Expected response is 401
    def test_get_nearest_invalid_token(self):
        with app.test_client() as client:
            requestData = {
                "location":    self.coords
            }

            rand_string = "assassin"
            hashed_token = hashlib.sha1(rand_string.encode()).hexdigest()

            hashed_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6InVzZXIxIiwicGFzc3dvcmQiOiJhOTk5M2UzNjQ3MDY4MTZhYmEzZTI1NzE3ODUwYzI2YzljZDBkODlkIiwiZXhwIjoxNTkwNzM1NDc0fQ.ulV8GclaJL_uHWLuWeTaEiGfRylTYxrqCUXLrMmzUF8"
            
            # send data as GET to endpoint
            response = client.get(
                '/api/tree/getNearestCluster',
                data=json.dumps(requestData),
                headers={"Content-Type": "application/json", "token": hashed_token}
            )
            self.assertEqual(
                response.status_code, 401
            )
    
    # TEST 11
    # Get nearest cluster
    # API is a GET method needing a token and location
    # Test doesn't send a token
    # Expected response is 400
    def test_get_nearest_without_token(self):
        with app.test_client() as client:
            # send data as GET to endpoint
            response = client.get(
                '/api/tree/getNearestCluster?location=' +str(self.coords)
            )
            self.assertEqual(
                response.status_code, 400
            )
    
    # TEST 12
    # Get nearest cluster
    # API is a GET method needing a token and location
    # Test doesn't send a token
    # Expected response is 400
    def test_get_nearest_without_location(self):
        with app.test_client() as client:
            # send data as GET to endpoint
            response = client.get(
                '/api/tree/getNearestCluster?token=' +self.logintoken
            )
            self.assertEqual(
                response.status_code, 400
            )
    
   

if __name__ == "__main__":
    unittest.main()
