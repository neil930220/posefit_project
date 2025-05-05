# classify/views.py

import os, json
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib.auth.decorators import login_required
from PIL import Image
import torch, cv2, numpy as np
from torchvision import transforms
import google.generativeai as genai
from torchvision import transforms, models, datasets
from .forms import PhotoForm
from dotenv import load_dotenv

# ── 1) ENV + Gemini setup ──
load_dotenv()
genai.configure(api_key=os.getenv("GENAI_API_KEY"))
gmodel = genai.GenerativeModel(model_name="gemini-2.0-flash")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = models.mobilenet_v2(pretrained=False)
model.classifier[1] = torch.nn.Linear(model.last_channel, 101)  # 101 TW-Food101 classes

model_path = os.path.join(settings.BASE_DIR, "models", "TW_Food101_MobileNetV2.pt")
state = torch.load(model_path, map_location=device)
model.load_state_dict(state)
model.to(device).eval()

# 2) Preprocessing pipeline
transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
    # add normalization here if needed
])

with open(os.path.join(settings.BASE_DIR, "models","class_names.json")) as f:
    class_names = json.load(f)

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
            photo.user = request.user if request.user.is_authenticated else None
            photo.save()

            # stash for the next step
            request.session['photo_id'] = photo.id
            return redirect('analyzing_page')

    else:
        form = PhotoForm()

    return render(request, 'index.html', {'form': form})

# classify/views.py

import json, re
from django.shortcuts import get_object_or_404, redirect
from .models import Photo
from django.http import JsonResponse

def analyzing_page(request):
    photo_id = request.session.get('photo_id')
    if not photo_id:
        return redirect('upload')

    photo = get_object_or_404(Photo, id=photo_id)
    image_path = photo.image.path
    file_url   = photo.image.url

    # ── **Heavy work happens here** ── #

    # 1) Classification
    img = Image.open(image_path).convert("RGB")
    inp = transform(img).unsqueeze(0).to(device)
    with torch.no_grad():
        logits = model(inp)
        probs  = torch.softmax(logits, dim=1)
        idx    = probs.argmax(dim=1).item()
        label  = class_names[idx].replace("_", " ")
        conf   = probs[0, idx].item()

    # 2) Area ratio
    arr = np.array(img)[:,:,::-1]
    gray = cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    _, th = cv2.threshold(blur, 100, 255, cv2.THRESH_BINARY)
    ctrs, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    food_area  = max((cv2.contourArea(c) for c in ctrs), default=0)
    image_area = arr.shape[0] * arr.shape[1]
    ratio = food_area / image_area

    # 3) Gemini prompt & response
    desc = (
        f"這張圖片中的食物預測為「{label}」，"
        f"其主要物體約佔整張圖片的 {ratio:.1%}。"
        "請依據這些資訊推測出可能熱量與營養素組成，簡單回應即可。"
    )
    gemini_resp = gmodel.generate_content(desc).text

    # 4) Parse calories
    m = re.search(r"(\d+)\s*(大卡|卡路里|kcal)?", gemini_resp)
    est_cal = int(m.group(1)) if m else 0

    # 5) Build payload
    detections = [{"item": label, "calories": est_cal}]
    result_data = {
        'file_url':        file_url,
        'prediction':      label,
        'confidence':      f"{conf:.2%}",
        'ratio':           f"{ratio:.2%}",
        'gemini':          gemini_resp,
        'detections': detections,
        'total_calories':  est_cal,
    }
    # stash for result view
    request.session['result_data'] = result_data

    return JsonResponse(result_data)





