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

4. Move into the `server` directory and type the following command to create `secret.key` file:
```sh
$ cd server
$ openssl rand 256 > secret.key
```

5. Move into the `frontend` directory and type the following command to make the frontend build:
```sh
$ cd frontend
$ npm run build
```

6. Keep Mongo running and start the server in the `server` directory:
```sh
$ python app.py --plant_initial_clusters=<boolean value> --tree_count=<integer value>
```

Open the link at the server's running port in the browser