import os


class Config:
    MONGO_URL = "mongodb://localhost:27017/"
    SERVER_SELECT_TIMEOUT = 3
    SECRET_KEY = "whatisgoingonhere"
    COLLECTION_LIST = ["user", "tree", "cluster"]
    ATTRIBUTES = {
        "user": ["username", "password", "address"],
        "tree": ["location"],
        "cluster": ["tree_list", "cluster"],
    }
