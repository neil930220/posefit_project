"""
Pose Detection Module using MediaPipe
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
    姿勢檢測器（優先使用 MediaPipe，備用 HOG）
    支援實時攝影鏡頭輸入和姿勢分析
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        初始化檢測器
        
        Args:
            model_path: 模型檔案路徑（可選）
        """
        self.model_path = model_path
        self.mp_pose = None
        self.pose = None
        self.keypoints = None
        self.confidence_threshold = 0.3
        
        # MediaPipe Pose 連接
        self.POSE_CONNECTIONS = [
            (11, 12),  # Left shoulder to Right shoulder
            (11, 13),  # Left shoulder to Left elbow
            (13, 15),  # Left elbow to Left wrist
            (12, 14),  # Right shoulder to Right elbow
            (14, 16),  # Right elbow to Right wrist
            (11, 23),  # Left shoulder to Left hip
            (12, 24),  # Right shoulder to Right hip
            (23, 24),  # Left hip to Right hip
            (23, 25),  # Left hip to Left knee
            (24, 26),  # Right hip to Right knee
            (25, 27),  # Left knee to Left ankle
            (26, 28),  # Right knee to Right ankle
        ]
        
        # 關鍵點名稱 (MediaPipe - 33個關鍵點)
        self.KEYPOINT_NAMES = [
            "Nose", "LEye", "REye", "LEar", "REar",
            "LShoulder", "RShoulder", "LElbow", "RElbow",
            "LWrist", "RWrist", "LPinky", "RPinky",
            "LIndex", "RIndex", "LThumb", "RThumb",
            "LHip", "RHip", "LKnee", "RKnee",
            "LAnkle", "RAnkle", "LHeel", "RHeel",
            "LFootIndex", "RFootIndex", "Navel", "Chest"
        ]
        
        self._load_model()
    
    def _load_model(self):
        """載入 MediaPipe 模型"""
        try:
            if MEDIAPIPE_AVAILABLE:
                self.mp_pose = mp.solutions.pose
                self.pose = self.mp_pose.Pose(
                    static_image_mode=False,
                    model_complexity=0,  # 使用最輕量級模型，最快速度
                    enable_segmentation=False,
                    smooth_landmarks=False,  # 關閉平滑，更快響應
                    min_detection_confidence=0.3,  # 最低檢測門檻
                    min_tracking_confidence=0.3   # 最低追蹤門檻
                )
                logger.info("MediaPipe Pose model loaded successfully (lightweight mode)")
            else:
                logger.warning("MediaPipe not available, using HOG fallback")
                self.pose = None
        except Exception as e:
            logger.error(f"Failed to load MediaPipe model: {e}")
            self.pose = None
    
    def detect_pose(self, frame: np.ndarray) -> Dict:
        """
        檢測單一幀的姿勢
        
        Args:
            frame: 輸入影像幀 (BGR 格式)
            
        Returns:
            包含關鍵點和姿勢資訊的字典
        """
        try:
            # 優先使用 MediaPipe
            if self.pose is not None:
                return self._mediapipe_detection(frame)
            else:
                # 備用 HOG 檢測
                return self._simple_pose_detection(frame)
        except Exception as e:
            logger.error(f"Pose detection failed: {e}")
            return self._fallback_pose_detection(frame)
    
    def _mediapipe_detection(self, frame: np.ndarray) -> Dict:
        """使用 MediaPipe 進行姿勢檢測"""
        # MediaPipe 需要 RGB 格式
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)
        
        if results.pose_landmarks:
            # 解析關鍵點
            keypoints = []
            for idx, landmark in enumerate(results.pose_landmarks.landmark):
                keypoints.append({
                    'id': idx,
                    'name': self.KEYPOINT_NAMES[idx] if idx < len(self.KEYPOINT_NAMES) else f"Point_{idx}",
                    'x': landmark.x,
                    'y': landmark.y,
                    'z': landmark.z,
                    'confidence': landmark.visibility
                })
            
            return {
                'keypoints': keypoints,
                'confidence': self._calculate_confidence(keypoints),
                'pose_score': self._calculate_pose_score(keypoints),
                'detected_errors': self._detect_pose_errors(keypoints),
                'timestamp': cv2.getTickCount() / cv2.getTickFrequency()
            }
        else:
            # 沒檢測到人體，使用 HOG 備用
            logger.info("MediaPipe no detection, using HOG fallback")
            return self._simple_pose_detection(frame)
    
    def _simple_pose_detection(self, frame: np.ndarray) -> Dict:
        """簡化的姿勢檢測"""
        # 使用多種方法提高檢測準確度
        boxes = []
        
        # 方法 1: HOG 人體檢測（更寬鬆的參數）
        try:
            hog = cv2.HOGDescriptor()
            hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
            detected_boxes, weights = hog.detectMultiScale(
                frame, 
                winStride=(4, 4),  # 更密集的步長
                padding=(8, 8),      # 更小的填充
                scale=1.02          # 更細的尺度變化
            )
            
            # 只保留高置信度的檢測
            for box, weight in zip(detected_boxes, weights):
                if weight > 0.3:  # 提高閾值
                    boxes.append(box)
        except Exception as e:
            logger.warning(f"HOG detection failed: {e}")
        
        # 方法 2: 如果 HOG 沒找到，使用預設位置
        if len(boxes) == 0:
            # 假設在影像中央有人
            h, w = frame.shape[:2]
            center_box = (w // 4, h // 6, w // 2, h * 2 // 3)  # x, y, width, height
            boxes.append(center_box)
            logger.info("使用預設人體框位置")
        
        # 選擇最大的人體框
        largest_box = max(boxes, key=lambda x: x[2] * x[3])
        keypoints = self._estimate_keypoints_from_box(largest_box, frame.shape)
        
        # 根據是否檢測到人體調整信心度
        confidence = 0.7 if len(boxes) > 0 else 0.5
        
        return {
            'keypoints': keypoints,
            'confidence': confidence,
            'pose_score': self._calculate_pose_score(keypoints),
            'detected_errors': self._detect_pose_errors(keypoints) if confidence > 0.6 else ['使用預設人體框，請確保全身在鏡頭中央'],
            'timestamp': cv2.getTickCount() / cv2.getTickFrequency()
        }
    
    def _fallback_pose_detection(self, frame: np.ndarray) -> Dict:
        """
        備用姿勢檢測方法
        """
        try:
            return self._simple_pose_detection(frame)
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
        
        keypoints = []
        
        # 簡化的關鍵點估計
        keypoint_positions = [
            (x + w // 2, y + h // 8, 'Nose'),      # 0: Nose
            (x + w // 2, y + h // 3, 'Neck'),      # 1: Neck
            (x + w // 4, y + h // 3, 'RShoulder'), # 2: RShoulder
            (x + w // 6, y + h // 2, 'RElbow'),    # 3: RElbow
            (x + w // 8, y + h // 1.5, 'RWrist'), # 4: RWrist
            (x + w * 3 // 4, y + h // 3, 'LShoulder'), # 5: LShoulder
            (x + w * 5 // 6, y + h // 2, 'LElbow'),    # 6: LElbow
            (x + w * 7 // 8, y + h // 1.5, 'LWrist'), # 7: LWrist
            (x + w // 2, y + h * 2 // 3, 'MidHip'),   # 8: MidHip
            (x + w // 3, y + h * 2 // 3, 'RHip'),     # 9: RHip
            (x + w // 4, y + h, 'RKnee'),          # 10: RKnee
            (x + w // 6, y + h, 'RAnkle'),         # 11: RAnkle
            (x + w * 2 // 3, y + h * 2 // 3, 'LHip'), # 12: LHip
            (x + w * 3 // 4, y + h, 'LKnee'),      # 13: LKnee
            (x + w * 5 // 6, y + h, 'LAnkle'),     # 14: LAnkle
        ]
        
        for i, (kx, ky, name) in enumerate(keypoint_positions):
            keypoints.append({
                'id': i,
                'name': name,
                'x': float(kx / width),
                'y': float(ky / height),
                'confidence': 0.8
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
        if len(visible_keypoints) < 8:
            errors.append("檢測到的關鍵點不足，請確保全身在鏡頭範圍內")
        
        # 檢查姿勢對稱性
        if self._check_posture_symmetry(keypoints):
            errors.append("檢測到身體不對稱，請保持平衡")
        
        return errors
    
    def _check_posture_symmetry(self, keypoints: List[Dict]) -> bool:
        """檢查姿勢對稱性"""
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
