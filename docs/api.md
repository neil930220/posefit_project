# FoodCam API Documentation

## Base URL
- Development: `http://localhost:8000`
- Production: `https://your-domain.com`

## Authentication

The API uses JWT (JSON Web Tokens) for authentication.

### Obtain Token
```http
POST /api/token/
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}
```

### Refresh Token
```http
POST /api/token/refresh/
Content-Type: application/json

{
    "refresh": "your_refresh_token"
}
```

### Using Token
Include the access token in the Authorization header:
```http
Authorization: Bearer your_access_token
```

## Endpoints

### Food Classification

#### Upload and Classify Food Image
```http
POST /classify/
Content-Type: multipart/form-data
Authorization: Bearer your_access_token

{
    "image": file
}
```

**Response:**
```json
{
    "food_type": "pizza",
    "confidence": 0.95,
    "calories": 285,
    "nutritional_info": {
        "protein": "12g",
        "carbs": "36g",
        "fat": "10g"
    },
    "area_percentage": 0.75
}
```

### User History

#### Get User History
```http
GET /api/history/
Authorization: Bearer your_access_token
```

#### Get Specific History Item
```http
GET /api/history/{id}/
Authorization: Bearer your_access_token
```

### User Management

#### User Registration
```http
POST /accounts/register/
Content-Type: application/json

{
    "username": "new_user",
    "email": "user@example.com",
    "password": "secure_password"
}
```

#### Password Reset
```http
POST /api/password_reset
Content-Type: application/json

{
    "email": "user@example.com"
}
```

## Error Responses

### 400 Bad Request
```json
{
    "error": "Invalid input data",
    "details": {
        "field": ["This field is required."]
    }
}
```

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 404 Not Found
```json
{
    "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
    "error": "Internal server error",
    "message": "Something went wrong on our end."
}
```

## Rate Limiting

- Anonymous users: 5 requests per minute
- Authenticated users: 10 requests per minute

## File Upload Limits

- Maximum file size: 10MB
- Supported formats: JPEG, PNG, WebP
- Recommended resolution: 224x224 to 1024x1024 pixels 