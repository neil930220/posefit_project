# classify/views.py

import os
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib.auth.decorators import login_required
from PIL import Image
import torch, cv2, numpy as np
from torchvision import transforms
import google.generativeai as genai
from .forms import PhotoForm
from dotenv import load_dotenv

# ── Move heavy initialization to module scope so it only happens once ── #

# 1) Load your model once
MODEL_PATH = os.path.join(settings.BASE_DIR, 'models', 'resnet18_food_demo.pt')
model_classifier = torch.load(MODEL_PATH, map_location='cpu', weights_only=False)
model_classifier.eval()

# 2) Preprocessing pipeline
transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
    # add normalization here if needed
])

load_dotenv()

# 3) Configure Gemini once
genai.configure(api_key=os.getenv("GENAI_API_KEY"))
gmodel = genai.GenerativeModel(model_name="gemini-2.0-flash")

class_names = [
    'stir-fried_calamari_broth',
    'papaya_milk',
    'stir-fried_loofah_with_clam'
]

# ── Your single, correct view ── #

# history: at the top of your views.py
import json
import re
from django.shortcuts import render
from .forms import PhotoForm
# … your other imports (PIL, torch, cv2, gmodel, etc.) …

def upload_image(request):
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            if request.user.is_authenticated:
                photo.user = request.user
            else:
                photo.user = None
            photo.save()

            # build URLs
            image_path = photo.image.path
            file_url   = photo.image.url

            # 1) Classification
            img = Image.open(image_path).convert("RGB")
            inp = transform(img).unsqueeze(0)
            with torch.no_grad():
                out  = model_classifier(inp)
                probs= torch.softmax(out, dim=1)
                idx  = torch.argmax(probs, dim=1).item()
                conf = probs[0][idx].item()
            label = class_names[idx]

            # 2) Area ratio
            arr = np.array(img)[:,:,::-1]
            gray = cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5,5), 0)
            _, th = cv2.threshold(blur, 100, 255, cv2.THRESH_BINARY)
            ctrs, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            food_area  = max((cv2.contourArea(c) for c in ctrs), default=0)
            image_area = arr.shape[0] * arr.shape[1]
            ratio = food_area / image_area

            # 3) Gemini nutrition text
            desc = (
                f"這張圖片中的食物預測為「{label}」，"
                f"其主要物體約佔整張圖片的 {ratio:.1%}。"
                "請依據這些資訊推測出可能熱量與營養素組成，簡單回應即可。"
            )
            gemini_resp = gmodel.generate_content(desc).text

            # 4) Parse calories (first integer in Gemini text)
            m = re.search(r"(\d+)\s*(大卡|卡路里|kcal)?", gemini_resp)
            estimated_calories = int(m.group(1)) if m else 0

            # 5) Build detections list
            detections = [{"item": label, "calories": estimated_calories}]
            total_calories = estimated_calories

            return render(request, 'result.html', {
                'file_url':        file_url,
                'prediction':      label,
                'confidence':      f"{conf:.2%}",
                'ratio':           f"{ratio:.2%}",
                'gemini':          gemini_resp,
                'detections_json': json.dumps(detections, ensure_ascii=False),
                'total_calories':  total_calories,
            })

    else:
        form = PhotoForm()

    return render(request, 'upload.html', {'form': form})


