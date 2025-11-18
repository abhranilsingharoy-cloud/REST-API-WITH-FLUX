# REST-API-WITH-FLUX
A advanced Flask REST API for managing user data with SQLite database, validation, pagination, and logging.

## Features

- **CRUD Operations**: Create, read, update, delete users
- **Database Integration**: SQLAlchemy with SQLite
- **Input Validation**: Comprehensive data validation
- **Pagination**: Support for large datasets
- **Filtering**: Filter users by active status and age range
- **Soft Delete**: Users can be restored after deletion
- **Error Handling**: Comprehensive error responses
- **Logging**: Rotating file logs for debugging
- **Health Check**: API status endpoint

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
```

1. Set environment variables in .env file
2. Run the application:
   ```bash
   python app.py
   ```

API Endpoints

Method Endpoint Description
GET /api/health Health check
GET /api/users Get all users (with pagination)
GET /api/users/<id> Get specific user
POST /api/users Create new user
PUT /api/users/<id> Update user
DELETE /api/users/<id> Soft delete user
PATCH /api/users/<id>/restore Restore user

Example Usage

Create User

```bash
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "age": 30
  }'
```

Get Users with Pagination

```bash
curl "http://localhost:5000/api/users?page=1&per_page=5&is_active=true"
```

Update User

```bash
curl -X PUT http://localhost:5000/api/users/<user_id> \
  -H "Content-Type: application/json" \
  -d '{"age": 31}'
```

```

## Advanced Features Included:

1. **Database Integration**: SQLAlchemy with SQLite for persistent storage
2. **Input Validation**: Comprehensive validation with custom error messages
3. **Pagination**: Support for large datasets with page/per_page parameters
4. **Filtering**: Filter users by active status and age range
5. **Soft Delete**: Users can be restored instead of permanent deletion
6. **Error Handling**: Custom error handlers with appropriate HTTP status codes
7. **Logging**: Rotating file logs for debugging and monitoring
8. **Environment Configuration**: Different configurations for development/production
9. **Health Check Endpoint**: API status monitoring
10. **RESTful Design**: Proper HTTP methods and status codes

## Testing with Postman:

1. **Create User**: POST to `http://localhost:5000/api/users`
2. **Get All Users**: GET to `http://localhost:5000/api/users`
3. **Get User by ID**: GET to `http://localhost:5000/api/users/<user_id>`
4. **Update User**: PUT to `http://localhost:5000/api/users/<user_id>`
5. **Delete User**: DELETE to `http://localhost:5000/api/users/<user_id>`
6. **Restore User**: PATCH to `http://localhost:5000/api/users/<user_id>/restore`
