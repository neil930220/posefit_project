#!/usr/bin/env python3
"""
Quick test to verify SETR-MLA model is working.
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
print("SETR-MLA Quick Test")
print("="*60)

# Load classifier
print("\n1. Loading classifier...")
classifier = get_foodseg103_classifier()
print("✓ Classifier loaded")

# Create a test image (random noise)
print("\n2. Creating test image (random noise)...")
test_image = Image.fromarray(np.random.randint(0, 255, (768, 768, 3), dtype=np.uint8))
print("✓ Test image created")

# Test with very low threshold
print("\n3. Testing prediction with threshold=0.05...")
predictions = classifier.predict(test_image, threshold=0.05)

if predictions:
    print(f"✓ Got {len(predictions)} predictions")
    print("\nTop 5 predictions:")
    for i, pred in enumerate(predictions[:5], 1):
        print(f"  {i}. {pred['name']}: {pred['confidence']:.4f}")
else:
    print("✗ No predictions returned")
    print("This indicates a problem with the model.")

print("\n" + "="*60)
print("Test complete!")
print("="*60)

