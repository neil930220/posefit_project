#!/usr/bin/env python3
"""
Test script to verify FoodSeg103 integration with Django backend.
Run this from the backend directory: python test_foodseg103_integration.py
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from ml_models.food_classifier import get_foodseg103_classifier
from PIL import Image
import requests
from io import BytesIO

def test_classifier_loading():
    """Test if the FoodSeg103 classifier loads correctly."""
    print("=" * 60)
    print("Test 1: Loading FoodSeg103 Classifier")
    print("=" * 60)
    
    try:
        classifier = get_foodseg103_classifier()
        print("✓ Classifier loaded successfully")
        print(f"  - Device: {classifier.device}")
        print(f"  - Threshold: {classifier.threshold}")
        print(f"  - Number of classes: {len(classifier.class_names)}")
        return classifier
    except Exception as e:
        print(f"✗ Failed to load classifier: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_prediction(classifier):
    """Test prediction with a sample image."""
    print("\n" + "=" * 60)
    print("Test 2: Making Predictions")
    print("=" * 60)
    
    # Create a simple test image (red square)
    test_img = Image.new('RGB', (224, 224), color=(255, 0, 0))
    
    try:
        predictions = classifier.predict(test_img, threshold=0.5)
        print(f"✓ Prediction successful")
        print(f"  - Number of detections: {len(predictions)}")
        
        if predictions:
            print("  - Top 5 predictions:")
            for i, pred in enumerate(predictions[:5]):
                print(f"    {i+1}. {pred['name']}: {pred['confidence']:.2%}")
        else:
            print("  - No food items detected (expected for test image)")
        
        return True
    except Exception as e:
        print(f"✗ Prediction failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_with_real_image():
    """Test with a real food image if available."""
    print("\n" + "=" * 60)
    print("Test 3: Testing with Real Food Image (Optional)")
    print("=" * 60)
    
    # Try to download a sample food image
    sample_url = "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400"
    
    try:
        print("Downloading sample food image...")
        response = requests.get(sample_url, timeout=5)
        img = Image.open(BytesIO(response.content)).convert('RGB')
        print("✓ Sample image downloaded")
        
        classifier = get_foodseg103_classifier()
        predictions = classifier.predict(img, threshold=0.7)
        
        print(f"✓ Prediction successful")
        print(f"  - Number of detections: {len(predictions)}")
        
        if predictions:
            print("  - Detected foods:")
            for pred in predictions:
                print(f"    - {pred['name']}: {pred['confidence']:.2%}")
        else:
            print("  - No food items detected with threshold 0.7")
            
        return True
    except requests.exceptions.RequestException:
        print("⚠ Could not download sample image (network error, skipping)")
        return None
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("FoodSeg103 Integration Test Suite")
    print("=" * 60 + "\n")
    
    # Test 1: Load classifier
    classifier = test_classifier_loading()
    if not classifier:
        print("\n❌ Classifier loading failed. Cannot continue tests.")
        return False
    
    # Test 2: Basic prediction
    if not test_prediction(classifier):
        print("\n❌ Basic prediction test failed.")
        return False
    
    # Test 3: Real image (optional)
    test_with_real_image()
    
    print("\n" + "=" * 60)
    print("✓ All critical tests passed!")
    print("=" * 60)
    print("\nIntegration is ready. You can now:")
    print("1. Start the Django server: python manage.py runserver")
    print("2. Test the API endpoint: POST /api/classify/upload/")
    print("=" * 60 + "\n")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

