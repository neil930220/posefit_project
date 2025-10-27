"""
MediaPipe-based Pose Detection Module
"""

import cv2
import numpy as np
import json
import os
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import logging

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    import warnings
    warnings.warn("MediaPipe not available, using fallback detection")

logger = logging.getLogger(__name__)


class OpenPoseDetector:
    """
    MediaPipe 姿勢檢測器
    支援實時攝影鏡頭輸入和姿勢分析
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        初始化 MediaPipe 檢測器
        
        Args:
            model_path: 未使用（保持向後兼容）
        """
        self.model_path = model_path
        self.mp_pose = None
        self.pose = None
        self.keypoints = None
        self.confidence_threshold = 0.1
        
        # MediaPipe 關鍵點定義 (33 個關鍵點)
        self.POSE_CONNECTIONS = [
            # Face
            (0, 1), (1, 2), (2, 3), (3, 7),
            # Upper body
            (0, 4), (4, 5), (5, 6), (6, 8),
            (0, 7), (7, 9), (9, 10), (10, 11),
            (11, 12), (12, 13), (13, 14), (14, 15),
            (12, 24), (11, 23),
            # Lower body
            (12, 24), (24, 26), (26, 28), (28, 30), (30, 32),
            (11, 23), (23, 25), (25, 27), (27, 29), (29, 31),
            (24, 26), (23, 25), (26, 28), (25, 27)
        ]
        
        # 關鍵點名稱 (MediaPipe Pose 格式 - 33個關鍵點)
        self.KEYPOINT_NAMES = [
            "Nose",                              # 0
            "LEye", "REye",                      # 1-2
            "LEar", "REar",                       # 3-4
            "LShoulder", "RShoulder",            # 5-6
            "LElbow", "RElbow",                  # 7-8
            "LWrist", "RWrist",                  # 9-10
            "LPinky", "RPinky",                  # 11-12
            "LIndex", "RIndex",                  # 13-14
            "LThumb", "RThumb",                 # 15-16
            "LHip", "RHip",                     # 17-18
            "LKnee", "RKnee",                   # 19-20
            "LAnkle", "RAnkle",                 # 21-22
            "LHeel", "RHeel",                   # 23-24
            "LFootIndex", "RFootIndex",         # 25-26
            "LFootInner", "RFootInner",         # 27-28
            "LFootOuter", "RFootOuter",         # 29-30
            "LFootHeel", "RFootHeel"            # 31-32
        ]
        
        self._load_model()
    
    def _load_model(self):
        """載入 MediaPipe 模型"""
        try:
            if MEDIAPIPE_AVAILABLE:
                self.mp_pose = mp.solutions.pose
                self.pose = self.mp_pose.Pose(
                    static_image_mode=False,
                    model_complexity=1,
                    smooth_landmarks=True,
                    enable_segmentation=False,
                    smooth_segmentation=True,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
                logger.info("MediaPipe Pose model loaded successfully")
            else:
                logger.warning("MediaPipe not available, using fallback detection")
                self._load_fallback_model()
        except Exception as e:
            logger.error(f"Failed to load MediaPipe model: {e}")
            self._load_fallback_model()
    
    def _load_fallback_model(self):
        """載入備用檢測模型"""
        try:
            logger.warning("Using fallback pose detection")
            self.pose = None
        except Exception as e:
            logger.error(f"Failed to load fallback model: {e}")
            self.pose = None
    
    def detect_pose(self, frame: np.ndarray) -> Dict:
        """
        檢測單一幀的姿勢
        
        Args:
            frame: 輸入影像幀 (BGR 格式)
            
        Returns:
            包含關鍵點和姿勢資訊的字典
        """
        if self.pose is None:
            return self._fallback_pose_detection(frame)
        
        try:
            # MediaPipe 需要 RGB 格式
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 執行姿勢檢測
            results = self.pose.process(rgb_frame)
            
            # 解析結果
            keypoints = self._parse_mediapipe_results(results, frame.shape)
            
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
    
    def _parse_mediapipe_results(self, results, frame_shape: Tuple) -> List[Dict]:
        """解析 MediaPipe 輸出為關鍵點"""
        keypoints = []
        height, width = frame_shape[:2]
        
        if not results.pose_landmarks:
            return keypoints
        
        # MediaPipe 的關鍵點已經標準化到 [0, 1]
        for idx, landmark in enumerate(results.pose_landmarks.landmark):
            keypoints.append({
                'id': idx,
                'name': self.KEYPOINT_NAMES[idx] if idx < len(self.KEYPOINT_NAMES) else f"Point_{idx}",
                'x': landmark.x,
                'y': landmark.y,
                'z': landmark.z,
                'confidence': landmark.visibility
            })
        
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
            errors.append("No person detected")
            return errors
        
        # 檢查關鍵點可見性
        visible_keypoints = [kp for kp in keypoints if kp.get('confidence', 0) > 0.3]
        if len(visible_keypoints) < 10:
            errors.append("檢測到的關鍵點不足，請確保全身在鏡頭範圍內")
        
        # 檢查姿勢對稱性
        if self._check_posture_symmetry(keypoints):
            errors.append("檢測到身體不對稱，請保持平衡")
        
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
            if y_diff > 0.05:  # 5% 的影像高度差異
                return True
        
        return False
    
    def draw_pose(self, frame: np.ndarray, keypoints: List[Dict]) -> np.ndarray:
        """在影像上繪製姿勢骨架"""
        if not keypoints:
            return frame
        
        # 繪製骨架連接（先畫線，這樣點會在上面）
        for pair in self.POSE_CONNECTIONS:
            if pair[0] < len(keypoints) and pair[1] < len(keypoints):
                kp1 = keypoints[pair[0]]
                kp2 = keypoints[pair[1]]
                
                if (kp1.get('confidence', 0) > self.confidence_threshold and 
                    kp2.get('confidence', 0) > self.confidence_threshold):
                    
                    x1 = int(kp1['x'] * frame.shape[1])
                    y1 = int(kp1['y'] * frame.shape[0])
                    x2 = int(kp2['x'] * frame.shape[1])
                    y2 = int(kp2['y'] * frame.shape[0])
                    
                    # 使用較粗的線條，顏色為藍色
                    cv2.line(frame, (x1, y1), (x2, y2), (255, 100, 0), 3)
        
        # 繪製關鍵點（較大的圓點）
        for kp in keypoints:
            if kp.get('confidence', 0) > self.confidence_threshold:
                x = int(kp['x'] * frame.shape[1])
                y = int(kp['y'] * frame.shape[0])
                
                # 外圈（較大）
                cv2.circle(frame, (x, y), 8, (0, 255, 0), -1)
                # 內圈（較小）
                cv2.circle(frame, (x, y), 4, (0, 150, 0), -1)
        
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
