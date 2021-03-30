"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, Todos
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/to-do', methods=['GET'])
def get_todo():

    fav = Todos.query.all()
    all_favs = list(map(lambda x: x.serialize(), fav))

    return jsonify(all_favs), 200

@app.route('/post_todo', methods=['POST'])
def post_todo():

    request_body = request.get_json()
    fav = Todos(label=request_body["label"], done=request_body["done"])
    db.session.add(fav)
    db.session.commit()

    return jsonify("Added!"), 200

@app.route('/del_todo/<int:fid>', methods=['DELETE'])
def del_todo(fid):
    
    fav = Todos.query.get(fid)

    if fav is None:
        raise APIException('To-Do not found', status_code=404)
    db.session.delete(fav)
    db.session.commit()

    return jsonify("Deleted!!"), 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
