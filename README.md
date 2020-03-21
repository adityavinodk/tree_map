# WT-2 Mini Project
## Tree Plantation App
Flask-React app with MongoDB

## Installation
1. Clone the repository
```sh
$ git clone https://github.com/adityavinodk/tree_map.git
$ cd tree_map
```

2. Create a virtual environment (optional).

3. Install all requirements using pip:
```sh
$ pip install -r requirements.txt
```

4. Type the following command to create `secret.key` file in server directory:
```sh
$ cd server
$ openssl rand 256 > secret.key
```

5. Keep Mongo running and start the server -
```sh
$ python app.py
```