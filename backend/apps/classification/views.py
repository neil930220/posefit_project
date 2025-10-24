# app/classify/api.py

from PIL import Image
import cv2, numpy as np, re
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import google.generativeai as genai
import os, json, sys
from rest_framework.permissions import AllowAny 
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http import JsonResponse

# Add ml_models to path
sys.path.insert(0, os.path.join(settings.BASE_DIR, 'ml_models'))

from ml_models.food_classifier import get_foodseg103_classifier

# ── Load your model + pipeline once ──

# 1) Gemini setup
genai.configure(api_key=os.getenv("GENAI_API_KEY"))
gmodel = genai.GenerativeModel(model_name="gemini-2.0-flash")

# 2) Load FoodSeg103 classifier
classifier = get_foodseg103_classifier()

# ── The single combined endpoint ──

class UploadAndAnalyze(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [AllowAny]
    authentication_classes = []  # 不做任何認證

    def post(self, request, format=None):
        file_obj = request.data.get('image')
        if not file_obj:
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

        # 1) Load image
        img = Image.open(file_obj).convert("RGB")

        # 2) Multi-label Classification with FoodSeg103
        predictions = classifier.predict(img, threshold=0.8)
        
        if not predictions:
            return JsonResponse({'error': True, 'message': 'No food items detected'})

        # 3) Area ratio (for overall food area)
        arr   = np.array(img)[:,:,::-1]
        gray  = cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)
        blur  = cv2.GaussianBlur(gray, (5,5), 0)
        _, th = cv2.threshold(blur, 100, 255, cv2.THRESH_BINARY)
        ctrs, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        food_area  = max((cv2.contourArea(c) for c in ctrs), default=0)
        image_area = arr.shape[0] * arr.shape[1]
        ratio      = food_area / image_area
        
        # Get top prediction confidence
        top_confidence = predictions[0]['confidence']
        print(f"Top prediction: {predictions[0]['name']} ({top_confidence:.2%})")
        
        # Only proceed if we have reasonable confidence
        if top_confidence > 0.7:
            # 4) Format food names for Gemini
            food_names = [p['name'] for p in predictions]
            food_list_str = "、".join(food_names)
            
            # Gemini nutrition analysis for combined foods
            desc = (
                f"這張圖片中檢測到以下食物：「{food_list_str}」，"
                f"食物約佔整張圖片的 {ratio:.1%}。"
                "請依據這些食物提供整體的營養資訊（所有檢測到的食物的總和），請使用以下格式回覆："
                "熱量: [數字] 大卡\n"
                "碳水化合物: [數字] 克\n"
                "蛋白質: [數字] 克\n"
                "脂肪: [數字] 克\n"
                "維生素: [簡短描述主要維生素]\n"
                "礦物質: [簡短描述主要礦物質]"
            )
            gemini_resp = gmodel.generate_content(desc).text
            
            # Parse the structured response
            nutrition_data = {}
            for line in gemini_resp.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    nutrition_data[key.strip()] = value.strip()

            # Extract calories
            calories_str = nutrition_data.get('熱量', '0 大卡')
            calories_match = re.search(r'(\d+)', calories_str)
            est_cal = int(calories_match.group(1)) if calories_match else 0

            # Extract other nutrition values with safe regex
            def safe_extract_float(key, default='0'):
                value_str = nutrition_data.get(key, default)
                match = re.search(r'(\d+\.?\d*)', value_str)
                return float(match.group(1)) if match else 0.0

            # Build JSON response
            result_data = {
                'predictions': predictions,
                'ratio': f"{ratio:.2%}",
                'gemini': gemini_resp,
                'nutrition': {
                    'calories': est_cal,
                    'carbs': safe_extract_float('碳水化合物'),
                    'protein': safe_extract_float('蛋白質'),
                    'fat': safe_extract_float('脂肪'),
                    'vitamins': nutrition_data.get('維生素', ''),
                    'minerals': nutrition_data.get('礦物質', '')
                },
                'total_calories': est_cal,
            }
            return Response(result_data, status=status.HTTP_200_OK)
        
        return JsonResponse({'error': True, 'message': 'Low confidence detection'})

