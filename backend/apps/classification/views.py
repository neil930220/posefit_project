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

        # 2) Multi-label Classification with FoodSeg103 ResNet50+CBAM Attention
        # Using threshold 0.5 for good balance between precision and recall
        predictions = classifier.predict(img, threshold=0.5)
        
        # Debug logging
        print(f"[DEBUG] Predictions count: {len(predictions)}")
        if predictions:
            print(f"[DEBUG] Top 5 predictions:")
            for pred in predictions[:5]:
                print(f"  - {pred['name']}: {pred['confidence']:.4f}")
        else:
            print("[DEBUG] No predictions returned from model")
        
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
        
        # Only proceed if we have reasonable confidence (0 for testing)
        if top_confidence > 0.70:
            # 4) Format food names for Gemini
            food_names = [p['name'] for p in predictions]
            food_list_str = "、".join(food_names)
            
            # Gemini nutrition analysis for combined foods (request STRICT JSON)
            desc = (
                f"這張圖片中檢測到以下食物：「{food_list_str}」，"
                f"食物約佔整張圖片的 {ratio:.1%}。"
                "請根據這些食物提供『合計』的營養素，並且只回覆一段有效的 JSON（不要加入任何解說或前後文，也不要使用 Markdown 區塊）。\n"
                "欄位與單位請完全依下列結構輸出（數值請為數字型態，沒有資料請填 0）：\n"
                "{\n"
                "  \"calories_kcal\": 0,\n"
                "  \"macros\": {\n"
                "    \"carbs_g\": 0,\n"
                "    \"protein_g\": 0,\n"
                "    \"fat_g\": 0,\n"
                "    \"fiber_g\": 0,\n"
                "    \"sugar_g\": 0\n"
                "  },\n"
                "  \"fat_breakdown\": {\n"
                "    \"saturated_fat_g\": 0,\n"
                "    \"monounsaturated_fat_g\": 0,\n"
                "    \"polyunsaturated_fat_g\": 0,\n"
                "    \"trans_fat_g\": 0\n"
                "  },\n"
                "  \"cholesterol_mg\": 0,\n"
                "  \"sodium_mg\": 0,\n"
                "  \"potassium_mg\": 0,\n"
                "  \"minerals_mg\": {\n"
                "    \"calcium\": 0,\n"
                "    \"iron\": 0,\n"
                "    \"magnesium\": 0,\n"
                "    \"phosphorus\": 0,\n"
                "    \"zinc\": 0\n"
                "  },\n"
                "  \"vitamins\": {\n"
                "    \"vitamin_a_ug_rae\": 0,\n"
                "    \"vitamin_c_mg\": 0,\n"
                "    \"vitamin_d_ug\": 0,\n"
                "    \"vitamin_e_mg\": 0,\n"
                "    \"vitamin_k_ug\": 0,\n"
                "    \"thiamin_b1_mg\": 0,\n"
                "    \"riboflavin_b2_mg\": 0,\n"
                "    \"niacin_b3_mg\": 0,\n"
                "    \"vitamin_b6_mg\": 0,\n"
                "    \"folate_b9_ug_dfe\": 0,\n"
                "    \"vitamin_b12_ug\": 0\n"
                "  }\n"
                "}"
            )
            # Gemini request with safe fallback
            try:
                gemini_raw = gmodel.generate_content(desc)
                gemini_resp = getattr(gemini_raw, 'text', '') or ''
            except Exception as e:
                print(f"[WARN] Gemini analysis failed: {e}")
                gemini_resp = ''
            
            # Parse the structured response (prefer JSON, fallback to simple key:value lines)
            nutrition_data = {}
            advanced = None
            if gemini_resp:
                # Try JSON parse directly
                try:
                    advanced = json.loads(gemini_resp)
                except Exception:
                    # Try to extract JSON block within text if any
                    try:
                        start = gemini_resp.find('{')
                        end = gemini_resp.rfind('}')
                        if start != -1 and end != -1 and end > start:
                            advanced = json.loads(gemini_resp[start:end+1])
                    except Exception:
                        advanced = None

                if advanced is None:
                    # Fallback: parse simple key: value lines (old format)
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

            # Helpers to safely read from advanced JSON
            def get_num(obj, key, default=0.0):
                try:
                    val = obj.get(key, default)
                    return float(val) if isinstance(val, (int, float, str)) and str(val).strip() != '' else default
                except Exception:
                    return default

            def get_nested(obj, path, default=0.0):
                try:
                    cur = obj
                    for p in path:
                        cur = cur.get(p, {}) if isinstance(cur, dict) else {}
                    if isinstance(cur, (int, float)):
                        return float(cur)
                    if isinstance(cur, str):
                        m = re.search(r'(\d+\.?\d*)', cur)
                        return float(m.group(1)) if m else default
                    return default
                except Exception:
                    return default

            # Derive advanced fields if available
            advanced_out = None
            if isinstance(advanced, dict):
                advanced_out = {
                    'calories_kcal': get_num(advanced, 'calories_kcal', 0.0),
                    'macros': {
                        'carbs_g': get_nested(advanced, ['macros', 'carbs_g'], 0.0),
                        'protein_g': get_nested(advanced, ['macros', 'protein_g'], 0.0),
                        'fat_g': get_nested(advanced, ['macros', 'fat_g'], 0.0),
                        'fiber_g': get_nested(advanced, ['macros', 'fiber_g'], 0.0),
                        'sugar_g': get_nested(advanced, ['macros', 'sugar_g'], 0.0),
                    },
                    'fat_breakdown': {
                        'saturated_fat_g': get_nested(advanced, ['fat_breakdown', 'saturated_fat_g'], 0.0),
                        'monounsaturated_fat_g': get_nested(advanced, ['fat_breakdown', 'monounsaturated_fat_g'], 0.0),
                        'polyunsaturated_fat_g': get_nested(advanced, ['fat_breakdown', 'polyunsaturated_fat_g'], 0.0),
                        'trans_fat_g': get_nested(advanced, ['fat_breakdown', 'trans_fat_g'], 0.0),
                    },
                    'cholesterol_mg': get_num(advanced, 'cholesterol_mg', 0.0),
                    'sodium_mg': get_num(advanced, 'sodium_mg', 0.0),
                    'potassium_mg': get_num(advanced, 'potassium_mg', 0.0),
                    'minerals_mg': {
                        'calcium': get_nested(advanced, ['minerals_mg', 'calcium'], 0.0),
                        'iron': get_nested(advanced, ['minerals_mg', 'iron'], 0.0),
                        'magnesium': get_nested(advanced, ['minerals_mg', 'magnesium'], 0.0),
                        'phosphorus': get_nested(advanced, ['minerals_mg', 'phosphorus'], 0.0),
                        'zinc': get_nested(advanced, ['minerals_mg', 'zinc'], 0.0),
                    },
                    'vitamins': {
                        'vitamin_a_ug_rae': get_nested(advanced, ['vitamins', 'vitamin_a_ug_rae'], 0.0),
                        'vitamin_c_mg': get_nested(advanced, ['vitamins', 'vitamin_c_mg'], 0.0),
                        'vitamin_d_ug': get_nested(advanced, ['vitamins', 'vitamin_d_ug'], 0.0),
                        'vitamin_e_mg': get_nested(advanced, ['vitamins', 'vitamin_e_mg'], 0.0),
                        'vitamin_k_ug': get_nested(advanced, ['vitamins', 'vitamin_k_ug'], 0.0),
                        'thiamin_b1_mg': get_nested(advanced, ['vitamins', 'thiamin_b1_mg'], 0.0),
                        'riboflavin_b2_mg': get_nested(advanced, ['vitamins', 'riboflavin_b2_mg'], 0.0),
                        'niacin_b3_mg': get_nested(advanced, ['vitamins', 'niacin_b3_mg'], 0.0),
                        'vitamin_b6_mg': get_nested(advanced, ['vitamins', 'vitamin_b6_mg'], 0.0),
                        'folate_b9_ug_dfe': get_nested(advanced, ['vitamins', 'folate_b9_ug_dfe'], 0.0),
                        'vitamin_b12_ug': get_nested(advanced, ['vitamins', 'vitamin_b12_ug'], 0.0),
                    }
                }

            # Build JSON response (preserve backward-compatible fields)
            basic_carbs = safe_extract_float('碳水化合物') if advanced_out is None else advanced_out['macros']['carbs_g']
            basic_protein = safe_extract_float('蛋白質') if advanced_out is None else advanced_out['macros']['protein_g']
            basic_fat = safe_extract_float('脂肪') if advanced_out is None else advanced_out['macros']['fat_g']
            vitamins_text = nutrition_data.get('維生素', '')
            minerals_text = nutrition_data.get('礦物質', '')

            result_data = {
                'predictions': predictions,
                'ratio': f"{ratio:.2%}",
                'gemini': gemini_resp or '營養模型暫無回覆，已提供基本預測結果',
                'nutrition': {
                    'calories': est_cal if advanced_out is None else int(round(advanced_out['calories_kcal'] or 0)),
                    'carbs': basic_carbs,
                    'protein': basic_protein,
                    'fat': basic_fat,
                    'fiber': 0.0 if advanced_out is None else advanced_out['macros']['fiber_g'],
                    'sugar': 0.0 if advanced_out is None else advanced_out['macros']['sugar_g'],
                    'sodium_mg': 0.0 if advanced_out is None else advanced_out['sodium_mg'],
                    'cholesterol_mg': 0.0 if advanced_out is None else advanced_out['cholesterol_mg'],
                    'potassium_mg': 0.0 if advanced_out is None else advanced_out['potassium_mg'],
                    'fat_breakdown': None if advanced_out is None else advanced_out['fat_breakdown'],
                    'minerals_mg': None if advanced_out is None else advanced_out['minerals_mg'],
                    'vitamins_detail': None if advanced_out is None else advanced_out['vitamins'],
                    'vitamins': vitamins_text,
                    'minerals': minerals_text
                },
                'total_calories': est_cal if advanced_out is None else int(round(advanced_out['calories_kcal'] or 0)),
            }
            return Response(result_data, status=status.HTTP_200_OK)
        
        return JsonResponse({'error': True, 'message': 'Low confidence detection'})

