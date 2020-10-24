import datetime
import jwt
import json

# Returns token for authentication, adds token to usersession
def authenticateUser(db, username, password, key):
    payload = {
        "username": username,
        "password": password,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
    }
    token = jwt.encode(payload, key, algorithm="HS256").decode("utf-8")
    db.usersessions.insert_one({"token": token})
    return token


# Validates the token provided by user
def verifyUser(db, token, key):
    verified = False
    payload = {}
    try:
        payload = jwt.decode(token, key, algorithm="HS256")
        if db.usersessions.find_one({"token": token}) != None:
            verified = True
    except jwt.exceptions.InvalidSignatureError:
        verified = False
    except jwt.ExpiredSignatureError:
        verified = False
        if db.usersessions.find_one({"token": token}) != None:
            db.usersessions.delete_one({"token": token})
    return verified, payload


# Returns the user details after token is verified
def userDetails(db, payload):
    user_details = {}
    user = db.users.find_one({"username": payload["username"]})
    if user != None:
        user_details = {
            "username": user["username"],
            "id": user["_id"],
            "location": user["location"],
        }
    return user_details
