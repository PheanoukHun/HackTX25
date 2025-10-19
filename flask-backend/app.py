from flask import Flask, jsonify, request, session
from flask_cors import CORS
import os
import json
from ..db.dbManager import UserDatabase, encrypt_password # Import UserDatabase and encrypt_password

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'a_very_secret_key_for_session') # Needed for sessions
CORS(app, supports_credentials=True) # Allow credentials for session cookies

# Initialize database
DB_PASSWORD = os.getenv('DB_PASSWORD', 'my_super_secret_password')
db = UserDatabase(db_name='user.db', password=DB_PASSWORD)
db.create_table() # Ensure the table exists

@app.route('/')
def hello_world():
    return "Hello, World!"

@app.route('/api/register', methods=['POST'])
def register_user():
    user_data = request.get_json()
    if not user_data:
        return jsonify({"error": "Invalid JSON data"}), 400
    
    name = user_data.get('name')
    password = user_data.get('password') # Assuming password is part of registration
    if not name or not password:
        return jsonify({"error": "User name and password are required"}), 400

    if db.get_user(name):
        return jsonify({"error": f"User '{name}' already exists"}), 409

    # Set initial past_conversation_context for new users
    user_data['past_conversation_context'] = "This is a long string representing the past conversation context for a newly registered user."
    
    # Hash the password before saving
    user_data['password'] = encrypt_password(password)

    if db.save_user(user_data):
        return jsonify({"message": f"User '{name}' registered successfully"}), 201
    else:
        return jsonify({"error": f"Failed to register user '{name}'"}), 500

@app.route('/api/login', methods=['POST'])
def login_user():
    login_data = request.get_json()
    if not login_data:
        return jsonify({"error": "Invalid JSON data"}), 400
    
    name = login_data.get('name')
    password = login_data.get('password')
    
    if not name or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    user = db.get_user(name)
    
    # Compare hashed password
    if user and db.check_password(password, user.get('password_hash')):
        session['logged_in'] = True
        session['username'] = name
        # Return relevant user data for the frontend
        return jsonify({
            "message": "Login successful",
            "user": user # Return all user data, including past_conversation_context
        }), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401

@app.route('/api/logout', methods=['POST'])
def logout_user():
    session.pop('logged_in', None)
    session.pop('username', None)
    return jsonify({"message": "Logged out successfully"}), 200

@app.route('/api/user/<name>', methods=['GET'])
def get_user(name):
    user = db.get_user(name)
    if user:
        # Remove sensitive information like password_hash before sending to frontend
        user_display = {k: v for k, v in user.items() if k != 'password_hash'}
        return jsonify(user_display), 200
    else:
        return jsonify({"error": f"User '{name}' not found"}), 404

@app.route('/api/submit_form', methods=['POST'])
def submit_form():
    form_data = request.get_json()
    if not form_data:
        return jsonify({"error": "Invalid JSON data"}), 400

    name = form_data.get('name')
    password = form_data.get('password')

    if not name or not password:
        return jsonify({"error": "Name and password are required"}), 400

    # Check if user exists
    user = db.get_user(name)

    if user:
        # Update existing user's form data
        if db.update_user(name, form_data):
            return jsonify({"message": f"Form data for user '{name}' updated successfully"}), 200
        else:
            return jsonify({"error": f"Failed to update form data for user '{name}'"}), 500
    else:
        # Register new user with form data
        form_data['past_conversation_context'] = "This is a long string representing the past conversation context for a newly registered user."
        form_data['password_hash'] = encrypt_password(password) # Hash the password
        
        if db.save_user(form_data):
            return jsonify({"message": f"User '{name}' registered and form data saved successfully"}), 201
        else:
            return jsonify({"error": f"Failed to register user '{name}' and save form data"}), 500

@app.route('/api/user/<name>', methods=['PUT'])
def update_user(name):
    updated_data = request.get_json()
    if not updated_data:
        return jsonify({"error": "Invalid JSON data"}), 400
    
    # If password is being updated, hash it
    if 'password' in updated_data:
        updated_data['password_hash'] = encrypt_password(updated_data['password'])
        del updated_data['password'] # Remove plain password
    
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