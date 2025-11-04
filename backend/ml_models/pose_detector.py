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
        
        # MediaPipe Pose 連接（使用 MediaPipe 官方定義）
        self.POSE_CONNECTIONS = None  # MediaPipe 會自動處理
        
        # 關鍵點名稱 (MediaPipe - 33個關鍵點)
        self.KEYPOINT_NAMES = [
            "Nose", "LEye", "REye", "LEar", "REar",
            "LShoulder", "RShoulder", "LElbow", "RElbow",
            "LWrist", "RWrist", "LPinky", "RPinky",
            "LIndex", "RIndex", "LThumb", "RThumb",
            "LHip", "RHip", "LKnee", "RKnee",
            "LAnkle", "RAnkle", "LHeel", "RHeel",
            "LFootIndex", "RFootIndex"
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
    
    def detect_pose(self, frame: np.ndarray, exercise_type: str = "general") -> Dict:
        """
        檢測單一幀的姿勢
        
        Args:
            frame: 輸入影像幀 (BGR 格式)
            exercise_type: 運動類型（用於計算動作接近程度的分數）
            
        Returns:
            包含關鍵點和姿勢資訊的字典
        """
        try:
            # 優先使用 MediaPipe
            if self.pose is not None:
                return self._mediapipe_detection(frame, exercise_type)
            else:
                # 備用 HOG 檢測
                return self._simple_pose_detection(frame, exercise_type)
        except Exception as e:
            logger.error(f"Pose detection failed: {e}")
            return self._fallback_pose_detection(frame, exercise_type)
    
    def _mediapipe_detection(self, frame: np.ndarray, exercise_type: str = "general") -> Dict:
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
            
            # 根據運動類型計算動作接近程度的分數
            pose_score, confidence = self._calculate_exercise_pose_score(keypoints, exercise_type)
            
            return {
                'keypoints': keypoints,
                'confidence': confidence,  # 動作接近程度的信心度
                'pose_score': pose_score,  # 基於動作接近程度的分數
                'detected_errors': self._detect_pose_errors(keypoints),
                'timestamp': cv2.getTickCount() / cv2.getTickFrequency()
            }
        else:
            # 沒檢測到人體，使用 HOG 備用
            logger.info("MediaPipe no detection, using HOG fallback")
            return self._simple_pose_detection(frame, exercise_type)
    
    def _simple_pose_detection(self, frame: np.ndarray, exercise_type: str = "general") -> Dict:
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
        
        # 根據運動類型計算動作接近程度的分數
        pose_score, confidence = self._calculate_exercise_pose_score(keypoints, exercise_type)
        
        return {
            'keypoints': keypoints,
            'confidence': confidence,  # 動作接近程度的信心度
            'pose_score': pose_score,  # 基於動作接近程度的分數
            'detected_errors': self._detect_pose_errors(keypoints) if confidence > 0.6 else ['使用預設人體框，請確保全身在鏡頭中央'],
            'timestamp': cv2.getTickCount() / cv2.getTickFrequency()
        }
    
    def _fallback_pose_detection(self, frame: np.ndarray, exercise_type: str = "general") -> Dict:
        """
        備用姿勢檢測方法
        """
        try:
            return self._simple_pose_detection(frame, exercise_type)
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
        """計算姿勢分數（舊方法，基於關鍵點可見性）"""
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
    
    def _calculate_exercise_pose_score(self, keypoints: List[Dict], exercise_type: str) -> Tuple[float, float]:
        """
        根據運動類型計算動作接近程度的分數和信心度
        
        Args:
            keypoints: 關鍵點列表
            exercise_type: 運動類型名稱（如 "舉重", "深蹲", "伏地挺身" 等）
            
        Returns:
            (pose_score, confidence) 元組
            - pose_score: 基於動作接近程度的分數 (0-100)
            - confidence: 動作接近程度的信心度 (0-1)
        """
        if not keypoints:
            return (0.0, 0.0)
        
        # 檢查關鍵點的可見性（基礎檢查）
        visible_keypoints = [kp for kp in keypoints if kp.get('confidence', 0) > 0.3]
        if len(visible_keypoints) < 5:
            return (0.0, 0.0)  # 關鍵點不足，無法評分
        
        # 根據運動類型選擇評分邏輯
        exercise_type_lower = exercise_type.lower()
        
        if "舉重" in exercise_type or "weightlifting" in exercise_type_lower or "weight" in exercise_type_lower:
            return self._calculate_weightlifting_score(keypoints)
        elif "深蹲" in exercise_type or "squat" in exercise_type_lower:
            # 深蹲評分邏輯（可以之後實現）
            return self._calculate_general_score(keypoints)
        elif "伏地挺身" in exercise_type or "pushup" in exercise_type_lower or "push-up" in exercise_type_lower:
            # 伏地挺身評分邏輯（可以之後實現）
            return self._calculate_general_score(keypoints)
        else:
            # 一般運動，使用通用評分
            return self._calculate_general_score(keypoints)
    
    def _calculate_weightlifting_score(self, keypoints: List[Dict]) -> Tuple[float, float]:
        """
        計算舉重姿勢分數
        評分標準：上半身手保持垂直角度（肩膀到手腕接近90度）
        
        Returns:
            (pose_score, confidence) 元組
        """
        # 找到需要的關鍵點
        left_shoulder = next((kp for kp in keypoints if kp.get('name') == 'LShoulder'), None)
        right_shoulder = next((kp for kp in keypoints if kp.get('name') == 'RShoulder'), None)
        left_wrist = next((kp for kp in keypoints if kp.get('name') == 'LWrist'), None)
        right_wrist = next((kp for kp in keypoints if kp.get('name') == 'RWrist'), None)
        left_elbow = next((kp for kp in keypoints if kp.get('name') == 'LElbow'), None)
        right_elbow = next((kp for kp in keypoints if kp.get('name') == 'RElbow'), None)
        
        # 檢查關鍵點是否可用（信心度 > 0.3）
        valid_points = []
        
        if left_shoulder and left_wrist and left_shoulder.get('confidence', 0) > 0.3 and left_wrist.get('confidence', 0) > 0.3:
            valid_points.append(('left', left_shoulder, left_wrist, left_elbow))
        
        if right_shoulder and right_wrist and right_shoulder.get('confidence', 0) > 0.3 and right_wrist.get('confidence', 0) > 0.3:
            valid_points.append(('right', right_shoulder, right_wrist, right_elbow))
        
        if not valid_points:
            return (0.0, 0.0)  # 沒有足夠的關鍵點
        
        # 計算每個手臂的角度分數
        scores = []
        confidences = []
        
        for side, shoulder, wrist, elbow in valid_points:
            # 計算肩膀到手腕的向量
            # 垂直方向：從肩膀向下到手腕（y軸增加）
            # 水平方向：手腕相對肩膀的x偏移
            
            # 計算角度：理想情況是手臂垂直，即肩膀和手腕的x座標應該相近
            # 我們計算肩膀到手腕的向量，然後看它與垂直線的夾角
            dx = abs(wrist['x'] - shoulder['x'])  # 水平偏差
            dy = abs(wrist['y'] - shoulder['y'])  # 垂直距離
            
            if dy < 0.01:  # 避免除以零
                angle_score = 0.0
            else:
                # 計算與垂直線的夾角（以弧度為單位）
                angle_rad = np.arctan(dx / dy)
                angle_deg = np.degrees(angle_rad)
                
                # 理想角度是0度（完全垂直），允許偏差±15度
                # 如果角度在0-15度之間，給滿分；超過15度開始扣分
                if angle_deg <= 15:
                    angle_score = 100.0
                elif angle_deg <= 30:
                    # 15-30度之間，線性扣分
                    angle_score = 100.0 - (angle_deg - 15) * (50.0 / 15.0)  # 從100降到50
                elif angle_deg <= 45:
                    # 30-45度之間，繼續扣分
                    angle_score = 50.0 - (angle_deg - 30) * (30.0 / 15.0)  # 從50降到20
                else:
                    # 超過45度，分數很低
                    angle_score = max(0.0, 20.0 - (angle_deg - 45) * 0.5)
            
            scores.append(angle_score)
            
            # 信心度：使用肩膀和手腕的平均信心度
            conf = (shoulder.get('confidence', 0) + wrist.get('confidence', 0)) / 2.0
            confidences.append(conf)
        
        # 計算平均分數和信心度
        avg_score = sum(scores) / len(scores) if scores else 0.0
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return (min(100.0, max(0.0, avg_score)), min(1.0, max(0.0, avg_confidence)))
    
    def _calculate_general_score(self, keypoints: List[Dict]) -> Tuple[float, float]:
        """
        計算一般運動姿勢分數（當沒有特定評分邏輯時）
        
        Returns:
            (pose_score, confidence) 元組
        """
        if not keypoints:
            return (0.0, 0.0)
        
        # 基於關鍵點可見性和信心度的一般評分
        visible_count = len([kp for kp in keypoints if kp.get('confidence', 0) > 0.3])
        total_count = len(keypoints)
        
        visibility_score = (visible_count / total_count) * 100 if total_count > 0 else 0.0
        
        # 平均信心度
        confidences = [kp.get('confidence', 0) for kp in keypoints]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        # 姿勢分數基於可見性，信心度單獨返回
        pose_score = visibility_score
        
        return (min(100.0, max(0.0, pose_score)), min(1.0, max(0.0, avg_confidence)))
    
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
        """
        在影像上繪製姿勢骨架
        
        注意：此方法現在主要用於測試，實際生產環境中前端會直接繪製
        """
        if not keypoints:
            return frame
        
        # 簡化版的繪製
        # 繪製關鍵點
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
