#!/usr/bin/env python3
"""
Test script for SETR-MLA model integration.
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

import torch
from pathlib import Path
from PIL import Image
import numpy as np

def test_model_loading():
    """Test loading the SETR-MLA model."""
    print("=" * 60)
    print("Testing SETR-MLA Model Loading")
    print("=" * 60)
    
    try:
        from ml_models.food_classifier import get_foodseg103_classifier
        
        print("\n1. Loading SETR-MLA model...")
        classifier = get_foodseg103_classifier()
        
        print(f"   ✓ Model loaded successfully")
        print(f"   Device: {classifier.device}")
        print(f"   Model path: {classifier.model_path}")
        print(f"   Number of classes: {classifier.model.num_classes}")
        print(f"   Image size: {classifier.model.img_size}")
        
        # Test with a dummy image
        print("\n2. Testing with dummy image (768x768)...")
        dummy_image = Image.fromarray(np.random.randint(0, 255, (768, 768, 3), dtype=np.uint8))
        
        predictions = classifier.predict(dummy_image, threshold=0.3)
        print(f"   ✓ Prediction completed")
        print(f"   Number of detected foods: {len(predictions)}")
        
        if predictions:
            print("\n3. Top predictions:")
            for i, pred in enumerate(predictions[:5], 1):
                print(f"   {i}. {pred['name']}: {pred['confidence']:.4f}")
        else:
            print("\n3. No foods detected (threshold may be too high)")
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_model_architecture():
    """Test the model architecture without loading weights."""
    print("\n" + "=" * 60)
    print("Testing Model Architecture")
    print("=" * 60)
    
    try:
        from ml_models.foodseg103_model import create_model
        
        print("\n1. Creating SETR-MLA model...")
        model = create_model(
            model_name='setr_mla',
            num_classes=104,
            pretrained=False,
            img_size=768
        )
        
        print(f"   ✓ Model created successfully")
        
        # Count parameters
        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        
        print(f"\n2. Model statistics:")
        print(f"   Total parameters: {total_params:,}")
        print(f"   Trainable parameters: {trainable_params:,}")
        print(f"   Model size: ~{total_params * 4 / 1024 / 1024:.2f} MB (float32)")
        
        # Test forward pass with dummy input
        print(f"\n3. Testing forward pass...")
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model = model.to(device)
        model.eval()
        
        dummy_input = torch.randn(1, 3, 768, 768).to(device)
        
        with torch.no_grad():
            output = model(dummy_input)
            print(f"   ✓ Forward pass successful")
            print(f"   Input shape: {dummy_input.shape}")
            print(f"   Output shape: {output.shape}")
            
            # Test multilabel prediction
            probs = model.predict_multilabel(dummy_input)
            print(f"   Multilabel output shape: {probs.shape}")
        
        print("\n" + "=" * 60)
        print("✓ Architecture tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error during architecture testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def check_checkpoint():
    """Check if the checkpoint file exists and inspect it."""
    print("\n" + "=" * 60)
    print("Checking Checkpoint File")
    print("=" * 60)
    
    checkpoint_path = Path(__file__).parent.parent / 'SETR_MLA_ReLeM' / 'iter_80000.pth'
    
    print(f"\nCheckpoint path: {checkpoint_path}")
    
    if not checkpoint_path.exists():
        print(f"✗ Checkpoint file not found!")
        return False
    
    print(f"✓ Checkpoint file exists")
    
    # Get file size
    file_size = checkpoint_path.stat().st_size / (1024 * 1024)  # MB
    print(f"  File size: {file_size:.2f} MB")
    
    try:
        print("\nLoading checkpoint to inspect structure...")
        checkpoint = torch.load(checkpoint_path, map_location='cpu', weights_only=False)
        
        if isinstance(checkpoint, dict):
            print(f"  Checkpoint is a dictionary")
            print(f"  Keys: {list(checkpoint.keys())}")
            
            if 'state_dict' in checkpoint:
                state_dict = checkpoint['state_dict']
            elif 'model_state_dict' in checkpoint:
                state_dict = checkpoint['model_state_dict']
            else:
                state_dict = checkpoint
            
            # Print first few keys
            keys = list(state_dict.keys())
            print(f"\n  Total parameters in checkpoint: {len(keys)}")
            print(f"\n  First 10 keys:")
            for i, key in enumerate(keys[:10], 1):
                shape = state_dict[key].shape if hasattr(state_dict[key], 'shape') else 'N/A'
                print(f"    {i}. {key}: {shape}")
            
            if len(keys) > 10:
                print(f"    ... and {len(keys) - 10} more")
        else:
            print(f"  Checkpoint is not a dictionary (type: {type(checkpoint)})")
        
        print("\n✓ Checkpoint inspection completed")
        
    except Exception as e:
        print(f"\n✗ Error loading checkpoint: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("SETR-MLA Model Integration Test")
    print("=" * 60)
    
    # Run tests
    tests = [
        ("Checkpoint Inspection", check_checkpoint),
        ("Model Architecture", test_model_architecture),
        ("Model Loading", test_model_loading),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result for _, result in results)
    print("\n" + ("=" * 60))
    if all_passed:
        print("All tests passed! ✓")
    else:
        print("Some tests failed. Please review the output above.")
    print("=" * 60)

