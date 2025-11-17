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
        
        # 關鍵點名稱 (MediaPipe - 33個關鍵點，依官方順序)
        self.KEYPOINT_NAMES = [
            "Nose", "LeftEyeInner", "LeftEye", "LeftEyeOuter", "RightEyeInner", "RightEye", "RightEyeOuter",
            "LeftEar", "RightEar", "MouthLeft", "MouthRight",
            "LeftShoulder", "RightShoulder", "LeftElbow", "RightElbow",
            "LeftWrist", "RightWrist", "LeftPinky", "RightPinky",
            "LeftIndex", "RightIndex", "LeftThumb", "RightThumb",
            "LeftHip", "RightHip", "LeftKnee", "RightKnee",
            "LeftAnkle", "RightAnkle", "LeftHeel", "RightHeel",
            "LeftFootIndex", "RightFootIndex"
        ]
        
        self.ARM_KEYPOINT_NAMES = {
            'left': {'shoulder': 'LeftShoulder', 'elbow': 'LeftElbow', 'wrist': 'LeftWrist'},
            'right': {'shoulder': 'RightShoulder', 'elbow': 'RightElbow', 'wrist': 'RightWrist'},
        }
        self.ANGLE_TARGET = 90.0
        self.ANGLE_TOLERANCE = 15.0
        self.MIN_KEYPOINT_CONFIDENCE = 0.4
        self.MIN_SEGMENT_LENGTH = 0.05
        
        # 動作辨識狀態機（追蹤完整動作循環：垂直 -> 伸直 -> 垂直）
        # 狀態：'idle' -> 'at_vertical' -> 'at_extended' -> 'completed'
        self.action_state = {
            'left': 'idle',   # 左臂狀態
            'right': 'idle'   # 右臂狀態
        }
        self.EXTENDED_ANGLE_THRESHOLD = 150.0  # 伸直角度閾值（>150度視為伸直）
        self.VERTICAL_ANGLE_MIN = 75.0  # 垂直角度下限（90-15）
        self.VERTICAL_ANGLE_MAX = 105.0  # 垂直角度上限（90+15）

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
    
    def reset_action_state(self):
        """重置動作狀態機（用於開始新的訓練）"""
        self.action_state = {
            'left': 'idle',
            'right': 'idle'
        }
        logger.info("動作狀態機已重置")
    
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
            
            evaluation = self._evaluate_weightlifting_pose(keypoints)

            return {
                'keypoints': keypoints,
                'confidence': evaluation['confidence'],
                'pose_score': evaluation['pose_score'],
                'is_success': evaluation['is_success'],
                'angles': evaluation['angles'],
                'detected_errors': evaluation['warnings'],
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
        used_default_box = False
        
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
            used_default_box = True
            logger.info("使用預設人體框位置")
        
        # 選擇最大的人體框
        largest_box = max(boxes, key=lambda x: x[2] * x[3])
        keypoints = self._estimate_keypoints_from_box(largest_box, frame.shape)
        
        evaluation = self._evaluate_weightlifting_pose(keypoints)
        warnings = list(evaluation['warnings'])
        if used_default_box:
            warnings.append('使用預設人體框，請確保全身在鏡頭中央。')
            evaluation['confidence'] *= 0.5

        return {
            'keypoints': keypoints,
            'confidence': evaluation['confidence'],
            'pose_score': evaluation['pose_score'],
            'is_success': evaluation['is_success'],
            'angles': evaluation['angles'],
            'detected_errors': warnings,
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
                'is_success': False,
                'angles': {'left': None, 'right': None},
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
            (x + w // 4, y + h // 3, 'RightShoulder'), # 2: RShoulder
            (x + w // 6, y + h // 2, 'RightElbow'),    # 3: RElbow
            (x + w // 8, y + h // 1.5, 'RightWrist'), # 4: RWrist
            (x + w * 3 // 4, y + h // 3, 'LeftShoulder'), # 5: LShoulder
            (x + w * 5 // 6, y + h // 2, 'LeftElbow'),    # 6: LElbow
            (x + w * 7 // 8, y + h // 1.5, 'LeftWrist'), # 7: LWrist
            (x + w // 2, y + h * 2 // 3, 'MidHip'),   # 8: MidHip
            (x + w // 3, y + h * 2 // 3, 'RightHip'),     # 9: RHip
            (x + w // 4, y + h, 'RightKnee'),          # 10: RKnee
            (x + w // 6, y + h, 'RightAnkle'),         # 11: RAnkle
            (x + w * 2 // 3, y + h * 2 // 3, 'LeftHip'), # 12: LHip
            (x + w * 3 // 4, y + h, 'LeftKnee'),      # 13: LKnee
            (x + w * 5 // 6, y + h, 'LeftAnkle'),     # 14: LAnkle
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

    def _get_keypoint(self, keypoints: List[Dict], name: str) -> Optional[Dict]:
        """依名稱取得單一關鍵點"""
        return next((kp for kp in keypoints if kp.get('name') == name), None)

    def _compute_elbow_angle(self, shoulder: Dict, elbow: Dict, wrist: Dict) -> Optional[float]:
        """計算肩-肘-腕所形成的夾角（肘部角度）"""
        upper = np.array([shoulder['x'] - elbow['x'], shoulder['y'] - elbow['y']])
        lower = np.array([wrist['x'] - elbow['x'], wrist['y'] - elbow['y']])

        if np.linalg.norm(upper) < self.MIN_SEGMENT_LENGTH or np.linalg.norm(lower) < self.MIN_SEGMENT_LENGTH:
            return None

        cos_theta = np.dot(upper, lower) / (np.linalg.norm(upper) * np.linalg.norm(lower))
        cos_theta = float(np.clip(cos_theta, -1.0, 1.0))
        return float(np.degrees(np.arccos(cos_theta)))

    def _evaluate_weightlifting_pose(self, keypoints: List[Dict]) -> Dict:
        """評估舉重姿勢，追蹤完整動作循環（垂直 -> 伸直 -> 垂直）"""
        result = {
            'pose_score': 0.0,
            'confidence': 0.0,
            'angles': {'left': None, 'right': None},
            'is_success': False,
            'warnings': []
        }

        if not keypoints:
            result['warnings'].append('無法偵測到手臂關鍵點，請站在鏡頭正中央。')
            return result

        side_scores: List[float] = []
        confidences: List[float] = []
        completed_arms: List[str] = []  # 完成完整動作循環的手臂

        for side, names in self.ARM_KEYPOINT_NAMES.items():
            label = '左' if side == 'left' else '右'
            shoulder = self._get_keypoint(keypoints, names['shoulder'])
            elbow = self._get_keypoint(keypoints, names['elbow'])
            wrist = self._get_keypoint(keypoints, names['wrist'])

            logger.debug(
                'Weightlifting evaluation - %s臂: shoulder=%s, elbow=%s, wrist=%s',
                label, shoulder, elbow, wrist
            )

            if not all([shoulder, elbow, wrist]):
                result['warnings'].append(f"{label}臂關鍵點未完整偵測，請保持手臂在鏡頭中。")
                # 重置該手臂的狀態
                self.action_state[side] = 'idle'
                continue

            confidences_side = [shoulder.get('confidence', 0), elbow.get('confidence', 0), wrist.get('confidence', 0)]
            logger.debug(
                'Weightlifting evaluation - %s臂 confidences=%s (threshold=%.2f)',
                label, confidences_side, self.MIN_KEYPOINT_CONFIDENCE
            )
            if min(confidences_side) < self.MIN_KEYPOINT_CONFIDENCE:
                result['warnings'].append(f"{label}臂關節信心度不足 (最低 {self.MIN_KEYPOINT_CONFIDENCE:.2f})，請調整位置或光線。")
                # 重置該手臂的狀態
                self.action_state[side] = 'idle'
                continue

            angle = self._compute_elbow_angle(shoulder, elbow, wrist)
            logger.debug('Weightlifting evaluation - %s臂角度=%s, 當前狀態=%s', label, angle, self.action_state[side])
            if angle is None:
                result['warnings'].append(f"{label}臂角度無法計算，請伸直手臂並保持穩定。")
                # 重置該手臂的狀態
                self.action_state[side] = 'idle'
                continue

            result['angles'][side] = angle
            current_state = self.action_state[side]
            
            # 狀態機邏輯：追蹤完整動作循環
            # idle -> at_vertical -> at_extended -> completed (回到 vertical)
            if current_state == 'idle':
                # 等待達到垂直姿勢
                if self.VERTICAL_ANGLE_MIN <= angle <= self.VERTICAL_ANGLE_MAX:
                    self.action_state[side] = 'at_vertical'
                    logger.debug('%s臂：達到垂直姿勢，狀態轉換 idle -> at_vertical', label)
            elif current_state == 'at_vertical':
                # 從垂直到伸直
                if angle >= self.EXTENDED_ANGLE_THRESHOLD:
                    self.action_state[side] = 'at_extended'
                    logger.debug('%s臂：達到伸直姿勢，狀態轉換 at_vertical -> at_extended', label)
                elif angle < self.VERTICAL_ANGLE_MIN:
                    # 如果角度變小，可能回到 idle
                    self.action_state[side] = 'idle'
            elif current_state == 'at_extended':
                # 從伸直回到垂直（完成一次動作）
                if self.VERTICAL_ANGLE_MIN <= angle <= self.VERTICAL_ANGLE_MAX:
                    self.action_state[side] = 'completed'
                    completed_arms.append(side)
                    logger.debug('%s臂：完成一次動作循環！狀態轉換 at_extended -> completed', label)
                elif angle < self.VERTICAL_ANGLE_MIN:
                    # 如果角度變小太多，可能回到 idle
                    self.action_state[side] = 'idle'
            elif current_state == 'completed':
                # 完成後，準備下一次循環
                if angle >= self.EXTENDED_ANGLE_THRESHOLD:
                    # 如果又伸直了，重置狀態（可能在做下一次）
                    self.action_state[side] = 'at_extended'
                elif self.VERTICAL_ANGLE_MIN <= angle <= self.VERTICAL_ANGLE_MAX:
                    # 保持在垂直，準備下一次
                    self.action_state[side] = 'at_vertical'
                else:
                    # 其他情況，重置
                    self.action_state[side] = 'idle'

            # 計算姿勢分數（基於角度與目標的偏差）
            deviation = abs(angle - self.ANGLE_TARGET)
            side_score = max(0.0, 100.0 - deviation * 2.0)
            side_scores.append(side_score)
            confidences.append(sum(confidences_side) / len(confidences_side))

        # 如果至少有一隻手臂完成完整循環，標記為成功
        if completed_arms:
            result['is_success'] = True
            # 重置已完成的手臂狀態，準備下一次循環
            for arm in completed_arms:
                self.action_state[arm] = 'at_vertical'
            logger.info('動作完成！完成的手臂：%s', completed_arms)

        if side_scores:
            result['pose_score'] = sum(side_scores) / len(side_scores)
        if confidences:
            result['confidence'] = min(1.0, sum(confidences) / len(confidences))

        if not side_scores:
            result['warnings'].append('無法判定手臂角度，請將雙臂完全呈現在鏡頭中。')

        return result

    def get_pose_feedback(self, keypoints: List[Dict], exercise_type: str = "general") -> str:
        """生成舉重姿勢回饋建議"""
        if not keypoints:
            return '無法檢測到姿勢，請確保身體在鏡頭範圍內。'

        evaluation = self._evaluate_weightlifting_pose(keypoints)
        messages: List[str] = []

        if evaluation['confidence'] < 0.5:
            messages.append('姿勢檢測信心度較低，請調整位置或光線。')

        messages.extend(evaluation['warnings'])

        if evaluation['is_success']:
            return '姿勢良好，請繼續保持！'

        angles_messages = []
        for side, angle in evaluation['angles'].items():
            if angle is None:
                continue
            label = '左' if side == 'left' else '右'
            angles_messages.append(f"{label}臂角度約 {angle:.1f}°")
        if angles_messages:
            messages.append('，'.join(angles_messages) + '，請調整至接近垂直 (90°)。')

        if not messages:
            messages.append('請將雙臂舉起並保持垂直，以獲得準確判定。')

        unique_messages: List[str] = []
        seen = set()
        for msg in messages:
            if msg and msg not in seen:
                unique_messages.append(msg)
                seen.add(msg)

        return '；'.join(unique_messages)


# 全域檢測器實例
_pose_detector_instance = None


def get_pose_detector() -> OpenPoseDetector:
    """獲取全域姿勢檢測器實例"""
    global _pose_detector_instance
    if _pose_detector_instance is None:
        _pose_detector_instance = OpenPoseDetector()
    return _pose_detector_instance
