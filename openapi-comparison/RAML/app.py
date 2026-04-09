import importlib.machinery
import importlib.util
import pkgutil
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

if not hasattr(pkgutil, 'get_loader'):
    def get_loader(name):
        if name == '__main__':
            return importlib.machinery.SourceFileLoader(name, __file__)
        spec = importlib.util.find_spec(name)
        return spec.loader if spec is not None else None
    pkgutil.get_loader = get_loader

app = Flask(__name__)
CORS(app)

USERS = {
    1: {"id": 1, "name": "Alice Smith", "email": "alice@example.com"},
    2: {"id": 2, "name": "Bob Jones", "email": "bob@example.com"}
}
NEXT_ID = 3

@app.route('/')
def index():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'index.html')

@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify(list(USERS.values())), 200

@app.route('/api/users', methods=['POST'])
def create_user():
    global NEXT_ID
    body = request.get_json()
    if not body or 'name' not in body or 'email' not in body:
        return jsonify({"error": "Bad Request"}), 400
    
    user_id = NEXT_ID
    NEXT_ID += 1
    new_user = {
        "id": user_id,
        "name": body["name"],
        "email": body["email"]
    }
    USERS[user_id] = new_user
    return jsonify(new_user), 201

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    if user_id in USERS:
        return jsonify(USERS[user_id]), 200
    return jsonify({"error": "User not found"}), 404

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    if user_id in USERS:
        body = request.get_json()
        if body and "name" in body:
            USERS[user_id]["name"] = body["name"]
        if body and "email" in body:
            USERS[user_id]["email"] = body["email"]
        return jsonify(USERS[user_id]), 200
    return jsonify({"error": "User not found"}), 404

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    if user_id in USERS:
        del USERS[user_id]
        return '', 204
    return jsonify({"error": "User not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
