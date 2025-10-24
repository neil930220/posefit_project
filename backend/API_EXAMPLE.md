# FoodSeg103 API Usage Examples

## Endpoint

```
POST /api/classify/upload/
```

## Request Format

**Content-Type:** `multipart/form-data`

**Parameters:**
- `image` (file, required): The food image to classify

## Response Examples

### Example 1: Single Food Item

**Request:**
```bash
curl -X POST http://localhost:8000/api/classify/upload/ \
  -F "image=@pizza.jpg"
```

**Response (Success):**
```json
{
  "predictions": [
    {
      "name": "pizza",
      "confidence": 0.94
    }
  ],
  "ratio": "67.5%",
  "gemini": "熱量: 285 大卡\n碳水化合物: 33 克\n蛋白質: 12 克\n脂肪: 11 克\n維生素: 維生素 A, B群\n礦物質: 鈣、鐵",
  "nutrition": {
    "calories": 285,
    "carbs": 33.0,
    "protein": 12.0,
    "fat": 11.0,
    "vitamins": "維生素 A, B群",
    "minerals": "鈣、鐵"
  },
  "total_calories": 285
}
```

### Example 2: Multiple Food Items (Salad)

**Request:**
```bash
curl -X POST http://localhost:8000/api/classify/upload/ \
  -F "image=@salad.jpg"
```

**Response (Success):**
```json
{
  "predictions": [
    {
      "name": "lettuce",
      "confidence": 0.92
    },
    {
      "name": "tomato",
      "confidence": 0.89
    },
    {
      "name": "cucumber",
      "confidence": 0.85
    },
    {
      "name": "carrot",
      "confidence": 0.81
    }
  ],
  "ratio": "54.3%",
  "gemini": "熱量: 65 大卡\n碳水化合物: 12 克\n蛋白質: 3 克\n脂肪: 0.5 克\n維生素: 維生素 A, C, K\n礦物質: 鉀、鎂",
  "nutrition": {
    "calories": 65,
    "carbs": 12.0,
    "protein": 3.0,
    "fat": 0.5,
    "vitamins": "維生素 A, C, K",
    "minerals": "鉀、鎂"
  },
  "total_calories": 65
}
```

### Example 3: Complex Meal

**Request:**
```bash
curl -X POST http://localhost:8000/api/classify/upload/ \
  -F "image=@meal_plate.jpg"
```

**Response (Success):**
```json
{
  "predictions": [
    {
      "name": "steak",
      "confidence": 0.91
    },
    {
      "name": "potato",
      "confidence": 0.88
    },
    {
      "name": "broccoli",
      "confidence": 0.86
    },
    {
      "name": "sauce",
      "confidence": 0.83
    },
    {
      "name": "carrot",
      "confidence": 0.79
    }
  ],
  "ratio": "72.1%",
  "gemini": "熱量: 520 大卡\n碳水化合物: 38 克\n蛋白質: 42 克\n脂肪: 18 克\n維生素: 維生素 A, B群, C\n礦物質: 鐵、鋅、鉀",
  "nutrition": {
    "calories": 520,
    "carbs": 38.0,
    "protein": 42.0,
    "fat": 18.0,
    "vitamins": "維生素 A, B群, C",
    "minerals": "鐵、鋅、鉀"
  },
  "total_calories": 520
}
```

### Example 4: No Food Detected

**Request:**
```bash
curl -X POST http://localhost:8000/api/classify/upload/ \
  -F "image=@landscape.jpg"
```

**Response (Error):**
```json
{
  "error": true,
  "message": "No food items detected"
}
```

### Example 5: Low Confidence Detection

**Request:**
```bash
curl -X POST http://localhost:8000/api/classify/upload/ \
  -F "image=@blurry_food.jpg"
```

**Response (Error):**
```json
{
  "error": true,
  "message": "Low confidence detection"
}
```

## Using with Python

```python
import requests

url = "http://localhost:8000/api/classify/upload/"

# Open and send image
with open("food_image.jpg", "rb") as f:
    files = {"image": f}
    response = requests.post(url, files=files)

if response.status_code == 200:
    data = response.json()
    
    # Check for errors
    if data.get("error"):
        print(f"Error: {data.get('message', 'Unknown error')}")
    else:
        # Print detected foods
        print("Detected foods:")
        for pred in data["predictions"]:
            print(f"  - {pred['name']}: {pred['confidence']*100:.1f}%")
        
        # Print nutrition
        nutrition = data["nutrition"]
        print(f"\nNutrition (combined):")
        print(f"  Calories: {nutrition['calories']} kcal")
        print(f"  Carbs: {nutrition['carbs']}g")
        print(f"  Protein: {nutrition['protein']}g")
        print(f"  Fat: {nutrition['fat']}g")
else:
    print(f"Request failed: {response.status_code}")
```

## Using with JavaScript/Fetch

```javascript
const formData = new FormData();
formData.append('image', imageFile); // imageFile is a File object

fetch('http://localhost:8000/api/classify/upload/', {
  method: 'POST',
  body: formData
})
  .then(response => response.json())
  .then(data => {
    if (data.error) {
      console.error('Error:', data.message);
    } else {
      console.log('Detected foods:', data.predictions);
      console.log('Nutrition:', data.nutrition);
      console.log('Total calories:', data.total_calories);
    }
  })
  .catch(error => console.error('Request failed:', error));
```

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `predictions` | Array | List of detected food items with confidence scores |
| `predictions[].name` | String | Name of the detected food class |
| `predictions[].confidence` | Float | Confidence score (0.0 to 1.0) |
| `ratio` | String | Percentage of image occupied by food |
| `gemini` | String | Raw response from Gemini AI about nutrition |
| `nutrition` | Object | Parsed nutrition information |
| `nutrition.calories` | Integer | Total calories in kcal |
| `nutrition.carbs` | Float | Carbohydrates in grams |
| `nutrition.protein` | Float | Protein in grams |
| `nutrition.fat` | Float | Fat in grams |
| `nutrition.vitamins` | String | Description of vitamins |
| `nutrition.minerals` | String | Description of minerals |
| `total_calories` | Integer | Same as nutrition.calories (legacy field) |
| `error` | Boolean | Present only on errors |
| `message` | String | Error message (present only on errors) |

## Notes

1. **Multi-label Detection**: The API now detects multiple food items in a single image
2. **Threshold**: Detection threshold is set to 0.8 (80% confidence) to reduce false positives
3. **Combined Nutrition**: Nutrition values represent the total/combined values for all detected foods
4. **Gemini AI**: Nutrition analysis is powered by Google's Gemini 2.0 Flash model
5. **Image Size**: Images are automatically resized to 224x224 for classification
6. **Supported Formats**: JPG, JPEG, PNG

## Common Issues

### Issue: All my images return "No food items detected"
**Solution**: The threshold might be too high. Contact the backend developer to adjust it from 0.8 to 0.7 in `views.py`.

### Issue: Getting too many incorrect predictions
**Solution**: The threshold might be too low. Contact the backend developer to increase it from 0.8 to 0.9.

### Issue: Gemini nutrition seems inaccurate
**Solution**: The Gemini model estimates based on typical portions. For precise tracking, use a food database instead.

