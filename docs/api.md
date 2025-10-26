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

### User History (FoodEntry)

Base path: `/api/history/entries/`

#### List History Entries
```http
GET /api/history/entries/?ordering=-created_at&date_from=2025-01-01&date_to=2025-12-31&calories_min=100&calories_max=1000&period=today
Authorization: Bearer your_access_token
```

Query params:
- `ordering`: `created_at`, `-created_at`, `total_calories`, `-total_calories`
- `date_from`, `date_to`: ISO 日期
- `period`: `today|yesterday|this_week|last_week|this_month|last_month`
- `calories_min`, `calories_max`: 數值

#### Create History Entry
```http
POST /api/history/entries/
Content-Type: multipart/form-data
Authorization: Bearer your_access_token

image: <file>
detections: [{"item":"bread","confidence":0.9,"calories":240,"carbs":40,"protein":8,"fat":3}] (as JSON string)
total_calories: 240
meal_type: breakfast
```

#### Update History Entry (owner only)
```http
PATCH /api/history/entries/{id}/
Content-Type: application/json
Authorization: Bearer your_access_token

{
  "detections": [
    {"item": "fried rice", "confidence": 0.91, "calories": 520, "carbs": 70, "protein": 12, "fat": 18}
  ],
  "total_calories": 520,
  "meal_type": "lunch"
}
```

Fields:
- `detections`: 陣列（每項至少含 `item`；其餘欄位可保留原值）
- `total_calories`: 整數
- `meal_type`: `breakfast|lunch|dinner` 或空字串

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