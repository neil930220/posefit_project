"""
Food classification module using PyTorch models.
"""

import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
import json
import os
from pathlib import Path
import numpy as np
import cv2


class FoodClassifier:
    """
    Food classification using pre-trained MobileNetV2 model.
    """
    
    def __init__(self, model_path=None, class_names_path=None):
        """
        Initialize the food classifier.
        
        Args:
            model_path (str): Path to the trained model file
            class_names_path (str): Path to the class names JSON file
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.class_names = []
        
        # Default paths
        if model_path is None:
            model_path = Path(__file__).parent / 'models' / 'TW_Food101_MobileNetV2.pt'
        if class_names_path is None:
            class_names_path = Path(__file__).parent / 'models' / 'class_names.json'
            
        self.model_path = model_path
        self.class_names_path = class_names_path
        
        # Image preprocessing transforms
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        self.load_model()
        self.load_class_names()
    
    def load_model(self):
        """Load the trained PyTorch model."""
        try:
            self.model = torch.load(self.model_path, map_location=self.device)
            self.model.eval()
            print(f"Model loaded successfully from {self.model_path}")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
    
    def load_class_names(self):
        """Load class names from JSON file."""
        try:
            with open(self.class_names_path, 'r') as f:
                self.class_names = json.load(f)
            print(f"Loaded {len(self.class_names)} class names")
        except Exception as e:
            print(f"Error loading class names: {e}")
            raise
    
    def preprocess_image(self, image):
        """
        Preprocess image for model input.
        
        Args:
            image: PIL Image or image path
            
        Returns:
            torch.Tensor: Preprocessed image tensor
        """
        if isinstance(image, str):
            image = Image.open(image).convert('RGB')
        elif hasattr(image, 'read'):
            # Handle file-like objects
            image = Image.open(image).convert('RGB')
        
        return self.transform(image).unsqueeze(0).to(self.device)
    
    def predict(self, image, top_k=5):
        """
        Predict food class for given image.
        
        Args:
            image: PIL Image, image path, or file-like object
            top_k (int): Number of top predictions to return
            
        Returns:
            list: List of tuples (class_name, confidence)
        """
        if self.model is None:
            raise ValueError("Model not loaded")
        
        # Preprocess image
        input_tensor = self.preprocess_image(image)
        
        # Make prediction
        with torch.no_grad():
            outputs = self.model(input_tensor)
            probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
        
        # Get top k predictions
        top_prob, top_indices = torch.topk(probabilities, top_k)
        
        predictions = []
        for i in range(top_k):
            class_idx = top_indices[i].item()
            confidence = top_prob[i].item()
            class_name = self.class_names[class_idx] if class_idx < len(self.class_names) else f"Unknown_{class_idx}"
            predictions.append((class_name, confidence))
        
        return predictions
    
    def get_best_prediction(self, image):
        """
        Get the best prediction for an image.
        
        Args:
            image: PIL Image, image path, or file-like object
            
        Returns:
            tuple: (class_name, confidence)
        """
        predictions = self.predict(image, top_k=1)
        return predictions[0] if predictions else ("Unknown", 0.0)


class FoodSeg103Classifier:
    """
    Multi-label food classification using FoodSeg103 ResNet50 with CBAM Attention.
    """
    
    def __init__(self, model_path=None, class_names_path=None, threshold=0.3):
        """
        Initialize the FoodSeg103 classifier.
        
        Args:
            model_path (str): Path to the trained model checkpoint
            class_names_path (str): Path to the class mapping JSON file
            threshold (float): Classification threshold for multi-label prediction
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.class_names = {}
        self.threshold = threshold
        
        # Default paths - using ResNet50 with CBAM Attention (trained on FoodSeg103)
        if model_path is None:
            model_path = Path(__file__).parent / 'models' / 'foodseg103_resnet50_attention.pth'
        if class_names_path is None:
            class_names_path = Path(__file__).parent / 'models' / 'foodseg103_classes.json'
            
        self.model_path = model_path
        self.class_names_path = class_names_path
        
        # Image preprocessing transforms (ImageNet normalization, same as training)
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        self.load_model()
        self.load_class_names()
    
    def load_model(self):
        """Load the trained ResNet50 with CBAM Attention model from checkpoint."""
        try:
            from .foodseg103_model import create_model
            
            # Create model architecture (ResNet50 with CBAM Attention)
            self.model = create_model(
                model_name='resnet50_attention',
                num_classes=103,
                pretrained=False,
                dropout=0.3  # Same dropout as training
            )
            
            # Load checkpoint with compatibility for PyTorch 2.6 weights_only default
            print(f"Loading checkpoint from: {self.model_path}")
            try:
                checkpoint = torch.load(self.model_path, map_location=self.device)
            except Exception as e:
                # If running on PyTorch >= 2.6, weights_only=True can cause failures for legacy checkpoints
                # Retry with weights_only=False if available
                try:
                    checkpoint = torch.load(self.model_path, map_location=self.device, weights_only=False)
                except TypeError:
                    # Older torch without weights_only arg, re-raise original
                    raise e
                except Exception:
                    raise
            
            # Load model state dict
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model = self.model.to(self.device)
            self.model.eval()
            
            # Print checkpoint info if available
            if 'epoch' in checkpoint:
                print(f"Loaded model trained for {checkpoint['epoch']} epochs")
            if 'best_mAP' in checkpoint:
                print(f"Model best mAP: {checkpoint['best_mAP']:.4f}")
            
            print(f"FoodSeg103 ResNet50+Attention model loaded successfully from {self.model_path}")
        except Exception as e:
            print(f"Error loading ResNet50 Attention model: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def load_class_names(self):
        """Load class names from JSON file."""
        try:
            with open(self.class_names_path, 'r') as f:
                self.class_names = json.load(f)
            print(f"Loaded {len(self.class_names)} FoodSeg103 class names")
        except Exception as e:
            print(f"Error loading class names: {e}")
            raise
    
    def preprocess_image(self, image):
        """
        Preprocess image for model input.
        
        Args:
            image: PIL Image or image path
            
        Returns:
            torch.Tensor: Preprocessed image tensor
        """
        if isinstance(image, str):
            image = Image.open(image).convert('RGB')
        elif hasattr(image, 'read'):
            # Handle file-like objects
            image = Image.open(image).convert('RGB')
        
        return self.transform(image).unsqueeze(0).to(self.device)
    
    def predict(self, image, threshold=None):
        """
        Predict food classes for given image (multi-label).
        
        Args:
            image: PIL Image, image path, or file-like object
            threshold (float): Classification threshold (uses instance threshold if None)
            
        Returns:
            list: List of dicts with 'name' and 'confidence' for detected foods
        """
        if self.model is None:
            raise ValueError("Model not loaded")
        
        if threshold is None:
            threshold = self.threshold
        
        # Preprocess image
        input_tensor = self.preprocess_image(image)
        
        # Make prediction
        with torch.no_grad():
            outputs = self.model(input_tensor)
            probabilities = torch.sigmoid(outputs).cpu().squeeze(0)
        
        # Get predictions above threshold
        predictions = []
        for idx in range(len(probabilities)):
            prob = probabilities[idx].item()
            if prob >= threshold:
                class_id = str(idx + 1)  # Class IDs start at 1 (0 is background)
                class_name = self.class_names.get(class_id, f"class_{class_id}")
                
                # Skip background class
                if class_name != "background":
                    predictions.append({
                        'name': class_name,
                        'confidence': prob
                    })
        
        
        # Sort by confidence (highest first)
        predictions.sort(key=lambda x: x['confidence'], reverse=True)
        
        return predictions
    
    def get_top_predictions(self, image, top_k=5, threshold=None):
        """
        Get top k predictions for an image.
        
        Args:
            image: PIL Image, image path, or file-like object
            top_k (int): Number of top predictions to return
            threshold (float): Classification threshold
            
        Returns:
            list: List of top k predictions
        """
        predictions = self.predict(image, threshold)
        return predictions[:top_k]


# Global classifier instances
_classifier_instance = None
_foodseg103_classifier_instance = None


def get_classifier():
    """
    Get or create a global classifier instance (legacy MobileNetV2).
    
    Returns:
        FoodClassifier: Global classifier instance
    """
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = FoodClassifier()
    return _classifier_instance


def get_foodseg103_classifier():
    """
    Get or create a global FoodSeg103 classifier instance.
    
    Returns:
        FoodSeg103Classifier: Global FoodSeg103 classifier instance
    """
    global _foodseg103_classifier_instance
    if _foodseg103_classifier_instance is None:
        _foodseg103_classifier_instance = FoodSeg103Classifier()
    return _foodseg103_classifier_instance 