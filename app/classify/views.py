# app/classify/api.py

from PIL import Image
import torch, cv2, numpy as np, re
from torchvision import transforms
from torchvision import models
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import google.generativeai as genai
import os, json
from rest_framework.permissions import AllowAny 
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http import JsonResponse

# ── Load your model + pipeline once ──

# 1) Gemini setup
genai.configure(api_key=os.getenv("GENAI_API_KEY"))
gmodel = genai.GenerativeModel(model_name="gemini-2.0-flash")

# 2) Torch device + model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = models.mobilenet_v2(pretrained=False)
model.classifier[1] = torch.nn.Linear(model.last_channel, 101)
state = torch.load(
    os.path.join(settings.BASE_DIR, "models", "TW_Food101_MobileNetV2.pt"),
    map_location=device
)
model.load_state_dict(state)
model.to(device).eval()

# 3) Transform + class names
transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
])
with open(os.path.join(settings.BASE_DIR, "models","class_names.json")) as f:
    class_names = json.load(f)

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
        inp = transform(img).unsqueeze(0).to(device)

        # 2) Classification
        with torch.no_grad():
            logits = model(inp)
            probs  = torch.softmax(logits, dim=1)
            idx    = probs.argmax(dim=1).item()
            label  = class_names[idx].replace("_", " ")
            conf   = probs[0, idx].item()

        # 3) Area ratio
        arr   = np.array(img)[:,:,::-1]
        gray  = cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)
        blur  = cv2.GaussianBlur(gray, (5,5), 0)
        _, th = cv2.threshold(blur, 100, 255, cv2.THRESH_BINARY)
        ctrs, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        food_area  = max((cv2.contourArea(c) for c in ctrs), default=0)
        image_area = arr.shape[0] * arr.shape[1]
        ratio      = food_area / image_area
        print(conf)
        if conf > 0.90 :     
            # 4) Gemini calorie guess
            desc = (
                f"這張圖片中的食物預測為「{label}」，"
                f"其主要物體約佔整張圖片的 {ratio:.1%}。"
                "請依據這些資訊提供以下營養資訊，請使用以下格式回覆："
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
            est_cal = int(re.search(r'(\d+)', calories_str).group(1))

            # Build JSON response
            result_data = {
                'prediction': label,
                'confidence': f"{conf:.2%}",
                'ratio': f"{ratio:.2%}",
                'gemini': gemini_resp,
                'nutrition': {
                    'calories': est_cal,
                    'carbs': float(re.search(r'(\d+\.?\d*)', nutrition_data.get('碳水化合物', '0')).group(1)),
                    'protein': float(re.search(r'(\d+\.?\d*)', nutrition_data.get('蛋白質', '0')).group(1)),
                    'fat': float(re.search(r'(\d+\.?\d*)', nutrition_data.get('脂肪', '0')).group(1)),
                    'vitamins': nutrition_data.get('維生素', ''),
                    'minerals': nutrition_data.get('礦物質', '')
                },
                'total_calories': est_cal,
            }
            return Response(result_data, status=status.HTTP_200_OK)
        return JsonResponse({'error': True})

