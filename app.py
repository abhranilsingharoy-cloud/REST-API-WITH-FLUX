from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory storage (List of dictionaries) as suggested in the hint
users = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"}
]

# Helper variable to auto-increment IDs
next_user_id = 3

# 1. GET - Retrieve all users
@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(users), 200

# 2. GET (Single) - Retrieve a specific user by ID
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = next((u for u in users if u['id'] == user_id), None)
    if user:
        return jsonify(user), 200
    return jsonify({"error": "User not found"}), 404

# 3. POST - Create a new user
@app.route('/users', methods=['POST'])
def create_user():
    global next_user_id
    data = request.get_json()
    
    if not data or 'name' not in data or 'email' not in data:
        return jsonify({"error": "Invalid data. Name and Email required"}), 400

    new_user = {
        "id": next_user_id,
        "name": data['name'],
        "email": data['email']
    }
    
    users.append(new_user)
    next_user_id += 1
    return jsonify(new_user), 201

# 4. PUT - Update an existing user
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = next((u for u in users if u['id'] == user_id), None)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json()
    
    # Update fields if they exist in the request
    user['name'] = data.get('name', user['name'])
    user['email'] = data.get('email', user['email'])
    
    return jsonify(user), 200

# 5. DELETE - Remove a user
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    global users
    user = next((u for u in users if u['id'] == user_id), None)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    users = [u for u in users if u['id'] != user_id]
    return jsonify({"message": "User deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
