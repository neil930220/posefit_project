#!/usr/bin/env python3
"""
Multi-label food classification models including SETR-MLA for semantic segmentation.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models
import timm
from collections import OrderedDict


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


class MLAHead(nn.Module):
    """Multi-Level Aggregation Head for SETR."""
    
    def __init__(self, mla_channels=256, mlahead_channels=128, num_classes=104):
        super(MLAHead, self).__init__()
        self.head2 = nn.Sequential(
            nn.Conv2d(mla_channels, mlahead_channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(mlahead_channels),
            nn.ReLU(),
            nn.Conv2d(mlahead_channels, mlahead_channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(mlahead_channels),
            nn.ReLU()
        )
        self.head3 = nn.Sequential(
            nn.Conv2d(mla_channels, mlahead_channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(mlahead_channels),
            nn.ReLU(),
            nn.Conv2d(mlahead_channels, mlahead_channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(mlahead_channels),
            nn.ReLU()
        )
        self.head4 = nn.Sequential(
            nn.Conv2d(mla_channels, mlahead_channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(mlahead_channels),
            nn.ReLU(),
            nn.Conv2d(mlahead_channels, mlahead_channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(mlahead_channels),
            nn.ReLU()
        )
        self.head5 = nn.Sequential(
            nn.Conv2d(mla_channels, mlahead_channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(mlahead_channels),
            nn.ReLU(),
            nn.Conv2d(mlahead_channels, mlahead_channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(mlahead_channels),
            nn.ReLU()
        )
        
        self.cls_seg = nn.Sequential(
            nn.Conv2d(4 * mlahead_channels, num_classes, 1)
        )
    
    def forward(self, mla_p2, mla_p3, mla_p4, mla_p5):
        head2 = self.head2(mla_p2)
        head3 = self.head3(mla_p3)
        head4 = self.head4(mla_p4)
        head5 = self.head5(mla_p5)
        
        # Upsample to same size
        head2 = F.interpolate(head2, size=head2.shape[-2:], mode='bilinear', align_corners=False)
        head3 = F.interpolate(head3, size=head2.shape[-2:], mode='bilinear', align_corners=False)
        head4 = F.interpolate(head4, size=head2.shape[-2:], mode='bilinear', align_corners=False)
        head5 = F.interpolate(head5, size=head2.shape[-2:], mode='bilinear', align_corners=False)
        
        # Concatenate
        x = torch.cat([head2, head3, head4, head5], dim=1)
        x = self.cls_seg(x)
        return x


class VIT_MLA(nn.Module):
    """Vision Transformer with Multi-Level Aggregation backbone for SETR."""
    
    def __init__(self, model_name='vit_base_patch16_224', img_size=768, num_classes=104,
                 embed_dim=768, depth=12, num_heads=12, mla_channels=256, 
                 mla_index=(5, 7, 9, 11)):
        super(VIT_MLA, self).__init__()
        
        # Load pretrained ViT
        self.vit = timm.create_model(model_name, pretrained=False, img_size=img_size, 
                                     num_classes=0)  # Remove classification head
        
        self.img_size = img_size
        self.embed_dim = embed_dim
        self.mla_index = mla_index
        
        # MLA projection layers - two-stage: 1x1 reduction then 3x3 conv
        # Stage 1: 1x1 convolution to reduce dimension from embed_dim to mla_channels
        self.mla_p2_1x1 = nn.Sequential(
            nn.Conv2d(embed_dim, mla_channels, 1, bias=False),
            nn.BatchNorm2d(mla_channels),
            nn.ReLU()
        )
        self.mla_p3_1x1 = nn.Sequential(
            nn.Conv2d(embed_dim, mla_channels, 1, bias=False),
            nn.BatchNorm2d(mla_channels),
            nn.ReLU()
        )
        self.mla_p4_1x1 = nn.Sequential(
            nn.Conv2d(embed_dim, mla_channels, 1, bias=False),
            nn.BatchNorm2d(mla_channels),
            nn.ReLU()
        )
        self.mla_p5_1x1 = nn.Sequential(
            nn.Conv2d(embed_dim, mla_channels, 1, bias=False),
            nn.BatchNorm2d(mla_channels),
            nn.ReLU()
        )
        
        # Stage 2: 3x3 convolution to refine features
        self.mla_p2 = nn.Sequential(
            nn.Conv2d(mla_channels, mla_channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(mla_channels),
            nn.ReLU()
        )
        self.mla_p3 = nn.Sequential(
            nn.Conv2d(mla_channels, mla_channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(mla_channels),
            nn.ReLU()
        )
        self.mla_p4 = nn.Sequential(
            nn.Conv2d(mla_channels, mla_channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(mla_channels),
            nn.ReLU()
        )
        self.mla_p5 = nn.Sequential(
            nn.Conv2d(mla_channels, mla_channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(mla_channels),
            nn.ReLU()
        )
    
    def forward(self, x):
        # Get multi-level features from ViT
        B = x.shape[0]
        H, W = self.img_size // 16, self.img_size // 16  # patch size = 16
        
        # Patch embedding
        x = self.vit.patch_embed(x)
        
        # Add position embedding (handle size mismatch by interpolation if needed)
        if x.shape[1] != self.vit.pos_embed.shape[1]:
            # Interpolate position embedding to match input size
            pos_embed = self.vit.pos_embed
            # Note: pos_embed has shape [1, num_patches + 1, embed_dim]
            # We need to resize it to match x which has shape [B, num_patches, embed_dim]
            # For now, we'll slice it to the right size
            if x.shape[1] < pos_embed.shape[1]:
                pos_embed = pos_embed[:, :x.shape[1], :]
            else:
                # Pad if needed (unlikely for our case)
                pos_embed = F.pad(pos_embed, (0, 0, 0, x.shape[1] - pos_embed.shape[1]))
        else:
            pos_embed = self.vit.pos_embed
        
        x = self.vit.pos_drop(x + pos_embed)
        
        # Forward through ViT blocks and collect intermediate features
        features = []
        for i, blk in enumerate(self.vit.blocks):
            x = blk(x)
            if i in self.mla_index:
                features.append(x)
        
        # Reshape features to 2D (remove cls token if present)
        mla_features = []
        for feat in features:
            # Check if cls token is present
            if feat.shape[1] == H * W + 1:
                feat = feat[:, 1:, :]  # Remove cls token
            feat = feat.permute(0, 2, 1).reshape(B, self.embed_dim, H, W)
            mla_features.append(feat)
        
        # Apply MLA projections (two stages: 1x1 then 3x3)
        mla_p2 = self.mla_p2(self.mla_p2_1x1(mla_features[0]))
        mla_p3 = self.mla_p3(self.mla_p3_1x1(mla_features[1]))
        mla_p4 = self.mla_p4(self.mla_p4_1x1(mla_features[2]))
        mla_p5 = self.mla_p5(self.mla_p5_1x1(mla_features[3]))
        
        return mla_p2, mla_p3, mla_p4, mla_p5


class SETR_MLA(nn.Module):
    """
    SETR with Multi-Level Aggregation for semantic segmentation.
    Can be used for multi-label classification by aggregating pixel predictions.
    """
    
    def __init__(self, num_classes=104, img_size=768, embed_dim=768, depth=12, 
                 num_heads=12, mla_channels=256, mlahead_channels=128, 
                 mla_index=(5, 7, 9, 11)):
        """
        Args:
            num_classes: Number of output classes (104 for FoodSeg103)
            img_size: Input image size
            embed_dim: ViT embedding dimension
            depth: Number of transformer blocks
            num_heads: Number of attention heads
            mla_channels: Number of channels in MLA layers
            mlahead_channels: Number of channels in MLA head
            mla_index: Indices of layers to extract features from
        """
        super(SETR_MLA, self).__init__()
        
        self.backbone = VIT_MLA(
            model_name='vit_base_patch16_224',
            img_size=img_size,
            num_classes=num_classes,
            embed_dim=embed_dim,
            depth=depth,
            num_heads=num_heads,
            mla_channels=mla_channels,
            mla_index=mla_index
        )
        
        self.decode_head = MLAHead(
            mla_channels=mla_channels,
            mlahead_channels=mlahead_channels,
            num_classes=num_classes
        )
        
        self.num_classes = num_classes
        self.img_size = img_size
    
    def forward(self, x):
        """
        Forward pass for segmentation.
        
        Args:
            x: Input images [batch_size, 3, H, W]
            
        Returns:
            Segmentation logits [batch_size, num_classes, H, W]
        """
        # Get multi-level features
        mla_p2, mla_p3, mla_p4, mla_p5 = self.backbone(x)
        
        # Decode to segmentation map
        seg_logits = self.decode_head(mla_p2, mla_p3, mla_p4, mla_p5)
        
        # Upsample to input size
        seg_logits = F.interpolate(seg_logits, size=(x.shape[2], x.shape[3]), 
                                   mode='bilinear', align_corners=False)
        
        return seg_logits
    
    def predict_multilabel(self, x, threshold=0.5):
        """
        Predict multi-label classification from segmentation output.
        
        Args:
            x: Input images [batch_size, 3, H, W]
            threshold: Threshold for class presence
            
        Returns:
            Multi-label predictions [batch_size, num_classes]
        """
        seg_logits = self.forward(x)
        
        # Apply softmax across classes for each pixel
        seg_probs = F.softmax(seg_logits, dim=1)
        
        # Global average pooling to get class-level predictions
        # Average across spatial dimensions
        class_probs = seg_probs.mean(dim=[2, 3])
        
        # Apply threshold
        predictions = (class_probs >= threshold).float()
        
        return class_probs  # Return probabilities for multi-label classification


def convert_mmseg_checkpoint(checkpoint):
    """
    Convert mmsegmentation checkpoint format to our model format.
    
    Args:
        checkpoint: The loaded checkpoint dictionary
        
    Returns:
        Converted state dictionary
    """
    if isinstance(checkpoint, dict):
        if 'state_dict' in checkpoint:
            state_dict = checkpoint['state_dict']
        elif 'model_state_dict' in checkpoint:
            state_dict = checkpoint['model_state_dict']
        else:
            state_dict = checkpoint
    else:
        state_dict = checkpoint
    
    # Convert keys from mmseg format to our format
    new_state_dict = OrderedDict()
    for k, v in state_dict.items():
        # Remove 'module.' prefix if present
        if k.startswith('module.'):
            k = k[7:]
        
        # Map mmseg keys to our model structure
        # Handle backbone.mla.mla_pX -> backbone.mla_pX
        if k.startswith('backbone.mla.mla_p'):
            # backbone.mla.mla_p2.0.weight -> backbone.mla_p2.0.weight
            # backbone.mla.mla_p2_1x1.0.weight -> backbone.mla_p2_1x1.0.weight
            new_key = k.replace('backbone.mla.', 'backbone.')
            new_state_dict[new_key] = v
        # mmseg: backbone.xxx (non-mla) -> our model: backbone.vit.xxx
        elif k.startswith('backbone.') and not k.startswith('backbone.mla'):
            # Extract the backbone part
            key_parts = k.split('.', 1)
            if len(key_parts) == 2:
                # backbone.something -> backbone.vit.something
                new_key = f"backbone.vit.{key_parts[1]}"
                new_state_dict[new_key] = v
            else:
                new_state_dict[k] = v
        # mmseg: decode_head.mlahead.headX -> our model: decode_head.headX
        elif k.startswith('decode_head.mlahead.'):
            new_key = k.replace('decode_head.mlahead.', 'decode_head.')
            new_state_dict[new_key] = v
        # mmseg: decode_head.conv_seg -> our model: decode_head.cls_seg.0
        elif k.startswith('decode_head.conv_seg.'):
            new_key = k.replace('decode_head.conv_seg.', 'decode_head.cls_seg.0.')
            new_state_dict[new_key] = v
        # Other decode_head keys
        elif k.startswith('decode_head.'):
            new_state_dict[k] = v
        # mmseg auxiliary_head -> skip for now (we don't use it for inference)
        elif k.startswith('auxiliary_head'):
            continue
        else:
            new_state_dict[k] = v
    
    return new_state_dict


def create_model(model_name='resnet50', num_classes=103, pretrained=True, dropout=0.5, **kwargs):
    """
    Factory function to create models.
    
    Args:
        model_name: Name of the model ('resnet50', 'efficientnet', 'swin', or 'setr_mla')
        num_classes: Number of output classes
        pretrained: If True, use pretrained weights
        dropout: Dropout probability
        **kwargs: Additional arguments for specific models (e.g., img_size for SETR)
        
    Returns:
        Model instance
    """
    if model_name.lower() == 'resnet50':
        return ResNet50MultiLabel(num_classes, pretrained, dropout)
    elif model_name.lower() == 'efficientnet':
        return EfficientNetMultiLabel(num_classes, pretrained, dropout)
    elif model_name.lower() == 'swin':
        return SwinTransformerMultiLabel(num_classes, pretrained, dropout)
    elif model_name.lower() == 'setr_mla':
        # SETR uses 104 classes (103 food + 1 background)
        img_size = kwargs.get('img_size', 768)
        return SETR_MLA(num_classes=num_classes, img_size=img_size)
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

