#!/usr/bin/env python3
"""
ResNet-50 based multi-label food classification model.
"""
import torch
import torch.nn as nn
from torchvision import models


class ResNet50MultiLabel(nn.Module):
    """
    ResNet-50 model for multi-label classification.
    """
    
    def __init__(self, num_classes=103, pretrained=True, dropout=0.5):
        """
        Args:
            num_classes: Number of output classes
            pretrained: If True, use pretrained ResNet-50 weights
            dropout: Dropout probability for regularization
        """
        super(ResNet50MultiLabel, self).__init__()
        
        # Load pretrained ResNet-50
        self.resnet = models.resnet50(pretrained=pretrained)
        
        # Get number of features from the last layer
        num_features = self.resnet.fc.in_features
        
        # Replace the final fully connected layer
        # For multi-label classification, we use sigmoid activation
        self.resnet.fc = nn.Sequential(
            nn.Dropout(p=dropout),
            nn.Linear(num_features, num_classes)
        )
        
        self.num_classes = num_classes
    
    def forward(self, x):
        """
        Forward pass.
        
        Args:
            x: Input images [batch_size, 3, H, W]
            
        Returns:
            Logits [batch_size, num_classes]
        """
        return self.resnet(x)
    
    def predict(self, x, threshold=0.5):
        """
        Make predictions with sigmoid activation.
        
        Args:
            x: Input images [batch_size, 3, H, W]
            threshold: Classification threshold
            
        Returns:
            Binary predictions [batch_size, num_classes]
        """
        logits = self.forward(x)
        probs = torch.sigmoid(logits)
        predictions = (probs >= threshold).float()
        return predictions


class EfficientNetMultiLabel(nn.Module):
    """
    EfficientNet-B0 model for multi-label classification (alternative).
    """
    
    def __init__(self, num_classes=103, pretrained=True, dropout=0.5):
        """
        Args:
            num_classes: Number of output classes
            pretrained: If True, use pretrained EfficientNet weights
            dropout: Dropout probability for regularization
        """
        super(EfficientNetMultiLabel, self).__init__()
        
        # Load pretrained EfficientNet-B0
        self.efficientnet = models.efficientnet_b0(pretrained=pretrained)
        
        # Get number of features from the classifier
        num_features = self.efficientnet.classifier[1].in_features
        
        # Replace the classifier
        self.efficientnet.classifier = nn.Sequential(
            nn.Dropout(p=dropout),
            nn.Linear(num_features, num_classes)
        )
        
        self.num_classes = num_classes
    
    def forward(self, x):
        return self.efficientnet(x)
    
    def predict(self, x, threshold=0.5):
        logits = self.forward(x)
        probs = torch.sigmoid(logits)
        predictions = (probs >= threshold).float()
        return predictions


class SwinTransformerMultiLabel(nn.Module):
    """
    Swin Transformer Tiny model for multi-label classification.
    """
    
    def __init__(self, num_classes=103, pretrained=True, dropout=0.5):
        """
        Args:
            num_classes: Number of output classes
            pretrained: If True, use pretrained Swin-T weights
            dropout: Dropout probability for regularization
        """
        super(SwinTransformerMultiLabel, self).__init__()
        
        # Load pretrained Swin Transformer Tiny
        self.swin = models.swin_t(pretrained=pretrained)
        
        # Get number of features from the classifier
        num_features = self.swin.head.in_features
        
        # Replace the classifier head
        self.swin.head = nn.Sequential(
            nn.Dropout(p=dropout),
            nn.Linear(num_features, num_classes)
        )
        
        self.num_classes = num_classes
    
    def forward(self, x):
        return self.swin(x)
    
    def predict(self, x, threshold=0.5):
        logits = self.forward(x)
        probs = torch.sigmoid(logits)
        predictions = (probs >= threshold).float()
        return predictions


def create_model(model_name='resnet50', num_classes=103, pretrained=True, dropout=0.5):
    """
    Factory function to create models.
    
    Args:
        model_name: Name of the model ('resnet50', 'efficientnet', or 'swin')
        num_classes: Number of output classes
        pretrained: If True, use pretrained weights
        dropout: Dropout probability
        
    Returns:
        Model instance
    """
    if model_name.lower() == 'resnet50':
        return ResNet50MultiLabel(num_classes, pretrained, dropout)
    elif model_name.lower() == 'efficientnet':
        return EfficientNetMultiLabel(num_classes, pretrained, dropout)
    elif model_name.lower() == 'swin':
        return SwinTransformerMultiLabel(num_classes, pretrained, dropout)
    else:
        raise ValueError(f"Unknown model: {model_name}")


if __name__ == "__main__":
    # Test the models
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Testing models on device: {device}\n")
    
    # Test all models
    for model_name in ['resnet50', 'efficientnet', 'swin']:
        print("="*60)
        print(f"Testing {model_name.upper()}")
        print("="*60)
        
        # Create model
        model = create_model(model_name, num_classes=103)
        model = model.to(device)
        
        # Test forward pass
        batch_size = 4
        dummy_input = torch.randn(batch_size, 3, 224, 224).to(device)
        
        print(f"Input shape: {dummy_input.shape}")
        
        # Forward pass
        output = model(dummy_input)
        print(f"Output shape: {output.shape}")
        
        # Predictions
        predictions = model.predict(dummy_input, threshold=0.5)
        print(f"Predictions shape: {predictions.shape}")
        print(f"Example prediction (first sample): {predictions[0].sum().item()} classes")
        
        # Count parameters
        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        print(f"Total parameters: {total_params:,}")
        print(f"Trainable parameters: {trainable_params:,}\n")

