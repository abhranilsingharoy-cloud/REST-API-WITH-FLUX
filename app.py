from flask import Flask, request, jsonify
from models import db, ma, User, user_schema, users_schema
from config import config
from werkzeug.security import generate_password_hash
import logging
from logging.handlers import RotatingFileHandler
import os

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    
    # Setup logging
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/api.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('User Management API startup')
    
    return app

app = create_app()

# Create database tables
with app.app_context():
    db.create_all()

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

# Utility functions
def validate_user_data(data, update=False):
    required_fields = ['username', 'email', 'first_name', 'last_name']
    
    if not update:
        for field in required_fields:
            if field not in data or not data[field]:
                return False, f'Missing required field: {field}'
    
    if 'email' in data and data['email']:
        # Basic email validation
        if '@' not in data['email']:
            return False, 'Invalid email format'
    
    if 'age' in data and data['age']:
        try:
            age = int(data['age'])
            if age < 0 or age > 150:
                return False, 'Age must be between 0 and 150'
        except ValueError:
            return False, 'Age must be a number'
    
    return True, 'Valid'

# Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users with optional filtering and pagination"""
    try:
        # Pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Filter parameters
        is_active = request.args.get('is_active', type=str)
        min_age = request.args.get('min_age', type=int)
        max_age = request.args.get('max_age', type=int)
        
        # Query building
        query = User.query
        
        if is_active is not None:
            query = query.filter(User.is_active == (is_active.lower() == 'true'))
        
        if min_age is not None:
            query = query.filter(User.age >= min_age)
        
        if max_age is not None:
            query = query.filter(User.age <= max_age)
        
        # Pagination
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        users = pagination.items
        
        return jsonify({
            'users': users_schema.dump(users),
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        })
    
    except Exception as e:
        app.logger.error(f'Error fetching users: {str(e)}')
        return jsonify({'error': 'Unable to fetch users'}), 500

@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user by ID"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user_schema.dump(user)})
    
    except Exception as e:
        app.logger.error(f'Error fetching user {user_id}: {str(e)}')
        return jsonify({'error': 'Unable to fetch user'}), 500

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No input data provided'}), 400
        
        # Validate input data
        is_valid, message = validate_user_data(data)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Check if username or email already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 409
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 409
        
        # Create new user
        new_user = User(
            username=data['username'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            age=data.get('age'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        app.logger.info(f'User created: {new_user.username}')
        return jsonify({
            'message': 'User created successfully',
            'user': user_schema.dump(new_user)
        }), 201
    
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error creating user: {str(e)}')
        return jsonify({'error': 'Unable to create user'}), 500

@app.route('/api/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    """Update an existing user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No input data provided'}), 400
        
        # Validate input data
        is_valid, message = validate_user_data(data, update=True)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Update user fields
        if 'username' in data and data['username'] != user.username:
            if User.query.filter_by(username=data['username']).first():
                return jsonify({'error': 'Username already exists'}), 409
            user.username = data['username']
        
        if 'email' in data and data['email'] != user.email:
            if User.query.filter_by(email=data['email']).first():
                return jsonify({'error': 'Email already exists'}), 409
            user.email = data['email']
        
        if 'first_name' in data:
            user.first_name = data['first_name']
        
        if 'last_name' in data:
            user.last_name = data['last_name']
        
        if 'age' in data:
            user.age = data['age']
        
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        db.session.commit()
        
        app.logger.info(f'User updated: {user.username}')
        return jsonify({
            'message': 'User updated successfully',
            'user': user_schema.dump(user)
        })
    
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error updating user {user_id}: {str(e)}')
        return jsonify({'error': 'Unable to update user'}), 500

@app.route('/api/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user (soft delete)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Soft delete by setting is_active to False
        user.is_active = False
        db.session.commit()
        
        app.logger.info(f'User deleted: {user.username}')
        return jsonify({'message': 'User deleted successfully'})
    
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error deleting user {user_id}: {str(e)}')
        return jsonify({'error': 'Unable to delete user'}), 500

@app.route('/api/users/<user_id>/restore', methods=['PATCH'])
def restore_user(user_id):
    """Restore a soft-deleted user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user.is_active = True
        db.session.commit()
        
        app.logger.info(f'User restored: {user.username}')
        return jsonify({
            'message': 'User restored successfully',
            'user': user_schema.dump(user)
        })
    
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error restoring user {user_id}: {str(e)}')
        return jsonify({'error': 'Unable to restore user'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
