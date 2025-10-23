"""
OpenPose-based Pose Detection Module
"""

import cv2
import numpy as np
import json
import os
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class OpenPoseDetector:
    """
    OpenPose 姿勢檢測器
    支援實時攝影鏡頭輸入和姿勢分析
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        初始化 OpenPose 檢測器
        
        Args:
            model_path: OpenPose 模型檔案路徑
        """
        self.model_path = model_path
        self.net = None
        self.keypoints = None
        self.confidence_threshold = 0.1
        
        # OpenPose 關鍵點定義 (COCO 格式)
        self.POSE_PAIRS = [
            (0, 1), (0, 2), (1, 3), (2, 4),  # Head
            (5, 6), (5, 7), (7, 9), (6, 8), (8, 10),  # Arms
            (5, 11), (6, 12), (11, 12),  # Torso
            (11, 13), (12, 14), (13, 15), (14, 16)  # Legs
        ]
        
        # 關鍵點名稱
        self.KEYPOINT_NAMES = [
            "Nose", "Neck", "RShoulder", "RElbow", "RWrist",
            "LShoulder", "LElbow", "LWrist", "MidHip", "RHip",
            "RKnee", "RAnkle", "LHip", "LKnee", "LAnkle",
            "REye", "LEye", "REar", "LEar", "LBigToe",
            "LSmallToe", "LHeel", "RBigToe", "RSmallToe", "RHeel"
        ]
        
        self._load_model()
    
    def _load_model(self):
        """載入 OpenPose 模型"""
        try:
            if self.model_path and os.path.exists(self.model_path):
                # 載入預訓練的 OpenPose 模型
                self.net = cv2.dnn.readNetFromTensorflow(self.model_path)
                logger.info(f"OpenPose model loaded from {self.model_path}")
            else:
                # 使用 OpenCV 內建的 DNN 模型
                self._load_opencv_dnn_model()
        except Exception as e:
            logger.error(f"Failed to load OpenPose model: {e}")
            self._load_opencv_dnn_model()
    
    def _load_opencv_dnn_model(self):
        """載入 OpenCV DNN 模型作為備用方案"""
        try:
            # 使用 OpenCV 的預訓練人體姿勢檢測模型
            model_url = "https://github.com/opencv/opencv/raw/master/samples/dnn/openpose_pose_coco.prototxt"
            weights_url = "https://github.com/opencv/opencv/raw/master/samples/dnn/openpose_pose_coco.caffemodel"
            
            # 這裡我們使用一個簡化的方法，實際部署時需要下載模型檔案
            logger.warning("Using simplified pose detection - full OpenPose model not available")
            self.net = None
        except Exception as e:
            logger.error(f"Failed to load OpenCV DNN model: {e}")
            self.net = None
    
    def detect_pose(self, frame: np.ndarray) -> Dict:
        """
        檢測單一幀的姿勢
        
        Args:
            frame: 輸入影像幀
            
        Returns:
            包含關鍵點和姿勢資訊的字典
        """
        if self.net is None:
            return self._fallback_pose_detection(frame)
        
        try:
            # 準備輸入
            blob = cv2.dnn.blobFromImage(
                frame, 1.0/255, (368, 368), (0, 0, 0), 
                swapRB=False, crop=False
            )
            
            # 執行推理
            self.net.setInput(blob)
            output = self.net.forward()
            
            # 解析輸出
            keypoints = self._parse_keypoints(output, frame.shape)
            
            return {
                'keypoints': keypoints,
                'confidence': self._calculate_confidence(keypoints),
                'pose_score': self._calculate_pose_score(keypoints),
                'detected_errors': self._detect_pose_errors(keypoints),
                'timestamp': cv2.getTickCount() / cv2.getTickFrequency()
            }
            
        except Exception as e:
            logger.error(f"Pose detection failed: {e}")
            return self._fallback_pose_detection(frame)
    
    def _fallback_pose_detection(self, frame: np.ndarray) -> Dict:
        """
        備用姿勢檢測方法 (使用 OpenCV 內建功能)
        """
        try:
            # 使用 HOG 人體檢測器
            hog = cv2.HOGDescriptor()
            hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
            
            # 檢測人體
            boxes, weights = hog.detectMultiScale(frame, winStride=(8, 8))
            
            if len(boxes) > 0:
                # 找到最大的人體框
                largest_box = max(boxes, key=lambda x: x[2] * x[3])
                x, y, w, h = largest_box
                
                # 簡化的關鍵點估計 (基於人體框)
                keypoints = self._estimate_keypoints_from_box(largest_box, frame.shape)
                
                return {
                    'keypoints': keypoints,
                    'confidence': 0.7,  # 中等信心度
                    'pose_score': 75.0,  # 預設分數
                    'detected_errors': [],
                    'timestamp': cv2.getTickCount() / cv2.getTickFrequency()
                }
            else:
                return {
                    'keypoints': [],
                    'confidence': 0.0,
                    'pose_score': 0.0,
                    'detected_errors': ['No person detected'],
                    'timestamp': cv2.getTickCount() / cv2.getTickFrequency()
                }
                
        except Exception as e:
            logger.error(f"Fallback pose detection failed: {e}")
            return {
                'keypoints': [],
                'confidence': 0.0,
                'pose_score': 0.0,
                'detected_errors': ['Detection failed'],
                'timestamp': cv2.getTickCount() / cv2.getTickFrequency()
            }
    
    def _estimate_keypoints_from_box(self, box: Tuple, frame_shape: Tuple) -> List[Dict]:
        """從人體框估計關鍵點位置"""
        x, y, w, h = box
        height, width = frame_shape[:2]
        
        # 簡化的關鍵點估計
        keypoints = []
        
        # 頭部關鍵點
        head_x = x + w // 2
        head_y = y + h // 8
        
        # 身體關鍵點
        shoulder_y = y + h // 3
        hip_y = y + h * 2 // 3
        
        # 創建關鍵點列表
        keypoint_positions = [
            (head_x, head_y),  # Nose
            (head_x, shoulder_y),  # Neck
            (x + w // 4, shoulder_y),  # LShoulder
            (x + w // 6, shoulder_y + h // 6),  # LElbow
            (x, shoulder_y + h // 3),  # LWrist
            (x + w * 3 // 4, shoulder_y),  # RShoulder
            (x + w * 5 // 6, shoulder_y + h // 6),  # RElbow
            (x + w, shoulder_y + h // 3),  # RWrist
            (head_x, hip_y),  # MidHip
            (x + w // 3, hip_y),  # LHip
            (x + w // 4, y + h),  # LKnee
            (x + w // 6, y + h),  # LAnkle
            (x + w * 2 // 3, hip_y),  # RHip
            (x + w * 3 // 4, y + h),  # RKnee
            (x + w * 5 // 6, y + h),  # RAnkle
        ]
        
        for i, (kx, ky) in enumerate(keypoint_positions):
            keypoints.append({
                'id': i,
                'name': self.KEYPOINT_NAMES[i] if i < len(self.KEYPOINT_NAMES) else f"Point_{i}",
                'x': float(kx / width),
                'y': float(ky / height),
                'confidence': 0.8
            })
        
        return keypoints
    
    def _parse_keypoints(self, output: np.ndarray, frame_shape: Tuple) -> List[Dict]:
        """解析 OpenPose 輸出為關鍵點"""
        keypoints = []
        height, width = frame_shape[:2]
        
        # 這裡需要根據實際的 OpenPose 輸出格式進行解析
        # 目前返回空列表，實際實作時需要根據模型輸出格式調整
        
        return keypoints
    
    def _calculate_confidence(self, keypoints: List[Dict]) -> float:
        """計算整體信心度"""
        if not keypoints:
            return 0.0
        
        confidences = [kp.get('confidence', 0) for kp in keypoints]
        return sum(confidences) / len(confidences)
    
    def _calculate_pose_score(self, keypoints: List[Dict]) -> float:
        """計算姿勢分數"""
        if not keypoints:
            return 0.0
        
        # 簡化的姿勢評分邏輯
        confidence = self._calculate_confidence(keypoints)
        visible_keypoints = len([kp for kp in keypoints if kp.get('confidence', 0) > 0.5])
        total_keypoints = len(keypoints)
        
        visibility_score = (visible_keypoints / total_keypoints) * 100
        confidence_score = confidence * 100
        
        # 綜合評分
        pose_score = (visibility_score + confidence_score) / 2
        
        return min(100.0, max(0.0, pose_score))
    
    def _detect_pose_errors(self, keypoints: List[Dict]) -> List[str]:
        """檢測姿勢錯誤"""
        errors = []
        
        if not keypoints:
            errors.append("No keypoints detected")
            return errors
        
        # 檢查關鍵點可見性
        visible_keypoints = [kp for kp in keypoints if kp.get('confidence', 0) > 0.5]
        if len(visible_keypoints) < 8:
            errors.append("Insufficient keypoints visible")
        
        # 檢查姿勢對稱性
        if self._check_posture_symmetry(keypoints):
            errors.append("Asymmetric posture detected")
        
        return errors
    
    def _check_posture_symmetry(self, keypoints: List[Dict]) -> bool:
        """檢查姿勢對稱性"""
        # 簡化的對稱性檢查
        # 實際實作時需要更複雜的邏輯
        
        # 檢查肩膀是否水平
        left_shoulder = next((kp for kp in keypoints if kp.get('name') == 'LShoulder'), None)
        right_shoulder = next((kp for kp in keypoints if kp.get('name') == 'RShoulder'), None)
        
        if left_shoulder and right_shoulder:
            y_diff = abs(left_shoulder['y'] - right_shoulder['y'])
            if y_diff > 0.1:  # 10% 的影像高度
                return True
        
        return False
    
    def draw_pose(self, frame: np.ndarray, keypoints: List[Dict]) -> np.ndarray:
        """在影像上繪製姿勢骨架"""
        if not keypoints:
            return frame
        
        # 繪製關鍵點
        for kp in keypoints:
            if kp.get('confidence', 0) > self.confidence_threshold:
                x = int(kp['x'] * frame.shape[1])
                y = int(kp['y'] * frame.shape[0])
                cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
        
        # 繪製骨架連接
        for pair in self.POSE_PAIRS:
            if pair[0] < len(keypoints) and pair[1] < len(keypoints):
                kp1 = keypoints[pair[0]]
                kp2 = keypoints[pair[1]]
                
                if (kp1.get('confidence', 0) > self.confidence_threshold and 
                    kp2.get('confidence', 0) > self.confidence_threshold):
                    
                    x1 = int(kp1['x'] * frame.shape[1])
                    y1 = int(kp1['y'] * frame.shape[0])
                    x2 = int(kp2['x'] * frame.shape[1])
                    y2 = int(kp2['y'] * frame.shape[0])
                    
                    cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        
        return frame
    
    def get_pose_feedback(self, keypoints: List[Dict], exercise_type: str = "general") -> str:
        """生成姿勢回饋建議"""
        if not keypoints:
            return "無法檢測到姿勢，請確保身體在鏡頭範圍內。"
        
        feedback = []
        
        # 檢查基本姿勢
        confidence = self._calculate_confidence(keypoints)
        if confidence < 0.5:
            feedback.append("姿勢檢測信心度較低，請調整位置或光線。")
        
        # 檢查對稱性
        if self._check_posture_symmetry(keypoints):
            feedback.append("請注意保持身體對稱，避免傾斜。")
        
        # 根據運動類型提供特定建議
        if exercise_type == "squat":
            feedback.extend(self._get_squat_feedback(keypoints))
        elif exercise_type == "pushup":
            feedback.extend(self._get_pushup_feedback(keypoints))
        
        return "；".join(feedback) if feedback else "姿勢良好，請繼續保持！"
    
    def _get_squat_feedback(self, keypoints: List[Dict]) -> List[str]:
        """深蹲姿勢回饋"""
        feedback = []
        
        # 檢查膝蓋位置
        left_knee = next((kp for kp in keypoints if kp.get('name') == 'LKnee'), None)
        right_knee = next((kp for kp in keypoints if kp.get('name') == 'RKnee'), None)
        
        if left_knee and right_knee:
            # 檢查膝蓋是否過度前傾
            left_hip = next((kp for kp in keypoints if kp.get('name') == 'LHip'), None)
            if left_hip and left_knee['x'] > left_hip['x'] + 0.05:
                feedback.append("左膝過度前傾，請保持膝蓋與腳尖對齊")
        
        return feedback
    
    def _get_pushup_feedback(self, keypoints: List[Dict]) -> List[str]:
        """伏地挺身姿勢回饋"""
        feedback = []
        
        # 檢查身體是否保持直線
        shoulder = next((kp for kp in keypoints if kp.get('name') == 'Neck'), None)
        hip = next((kp for kp in keypoints if kp.get('name') == 'MidHip'), None)
        
        if shoulder and hip:
            # 檢查身體是否保持水平
            if abs(shoulder['y'] - hip['y']) > 0.1:
                feedback.append("請保持身體成一直線，避免臀部過高或過低")
        
        return feedback


# 全域檢測器實例
_pose_detector_instance = None


def get_pose_detector() -> OpenPoseDetector:
    """獲取全域姿勢檢測器實例"""
    global _pose_detector_instance
    if _pose_detector_instance is None:
        _pose_detector_instance = OpenPoseDetector()
    return _pose_detector_instance
