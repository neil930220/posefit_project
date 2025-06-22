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


# Global classifier instance
_classifier_instance = None


def get_classifier():
    """
    Get or create a global classifier instance.
    
    Returns:
        FoodClassifier: Global classifier instance
    """
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = FoodClassifier()
    return _classifier_instance 