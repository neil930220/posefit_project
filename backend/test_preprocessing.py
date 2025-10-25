#!/usr/bin/env python3
"""
Test preprocessing with different image sizes.
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from PIL import Image
import numpy as np
from ml_models.food_classifier import get_foodseg103_classifier

print("="*60)
print("Testing Preprocessing with Different Image Sizes")
print("="*60)

# Load classifier
print("\n1. Loading classifier...")
classifier = get_foodseg103_classifier()
print("✓ Classifier loaded")

# Test different image sizes
test_sizes = [
    (428, 640, "Landscape"),  # Your error case
    (640, 428, "Portrait"),
    (768, 768, "Square 768x768"),
    (1024, 768, "Wide"),
    (300, 500, "Small portrait"),
    (2000, 1500, "Large landscape"),
]

for height, width, description in test_sizes:
    print(f"\n2. Testing {description} ({height}×{width})...")
    
    # Create test image
    test_image = Image.fromarray(
        np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
    )
    
    try:
        # Preprocess
        tensor = classifier.preprocess_image(test_image)
        print(f"   ✓ Preprocessed to shape: {tensor.shape}")
        
        # Verify shape is correct
        assert tensor.shape == (1, 3, 768, 768), f"Expected (1,3,768,768), got {tensor.shape}"
        
        # Test prediction
        predictions = classifier.predict(test_image, threshold=0.1)
        print(f"   ✓ Prediction successful, found {len(predictions)} items")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*60)
print("All tests completed!")
print("="*60)

