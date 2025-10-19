from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
from ..db.dbManager import UserDatabase # Import UserDatabase

app = Flask(__name__)
CORS(app)

# Initialize database
DB_PASSWORD = os.getenv('DB_PASSWORD', 'my_super_secret_password')
db = UserDatabase(db_name='user.db', password=DB_PASSWORD)
db.create_table() # Ensure the table exists

@app.route('/')
def hello_world():
    return "Hello, World!"

@app.route('/api/user', methods=['POST'])
def create_user():
    user_data = request.get_json()
    if not user_data:
        return jsonify({"error": "Invalid JSON data"}), 400
    
    name = user_data.get('name')
    if not name:
        return jsonify({"error": "User name is required"}), 400

    if db.save_user(user_data):
        return jsonify({"message": f"User '{name}' created successfully"}), 201
    else:
        return jsonify({"error": f"Failed to create user '{name}'"}), 500

@app.route('/api/user/<name>', methods=['GET'])
def get_user(name):
    user = db.get_user(name)
    if user:
        return jsonify(user), 200
    else:
        return jsonify({"error": f"User '{name}' not found"}), 404

@app.route('/api/user/<name>', methods=['PUT'])
def update_user(name):
    updated_data = request.get_json()
    if not updated_data:
        return jsonify({"error": "Invalid JSON data"}), 400
    
    if db.update_user(name, updated_data):
        return jsonify({"message": f"User '{name}' updated successfully"}), 200
    else:
        return jsonify({"error": f"Failed to update user '{name}'"}), 500

@app.route('/api/user/<name>/<field>', methods=['GET'])
def get_user_field(name, field):
    field_value = db.get_user_field(name, field)
    if field_value is not None:
        return jsonify({field: field_value}), 200
    else:
        return jsonify({"error": f"Field '{field}' for user '{name}' not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)