import os

class Config:
    MONGO_URL = 'mongodb://localhost:27017/'
    SECRET_KEY = 'whatisgoingonhere'
    COLLECTION_LIST = ['user', 'tree', 'cluster']
    ATTRIBUTES = {
        'user': ['username', 'password', 'address'],
        'tree': ['location'],
        'cluster': ['tree_list', 'cluster']
    }