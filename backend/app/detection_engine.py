import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
import os
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeepfakeDetectionEngine:
    """Advanced deepfake detection engine using multiple detection methods"""
    
    def __init__(self, model_path: str = "./models"):
        self.model_path = model_path
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
    def extract_frames(self, video_path: str, max_frames: int = 100) -> List[np.ndarray]:
        """Extract frames from video for analysis"""
        frames = []
        cap = cv2.VideoCapture(video_path)
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_interval = max(1, total_frames // max_frames)
        
        frame_count = 0
        while len(frames) < max_frames and frame_count < total_frames:
            ret, frame = cap.read()
            if ret and frame_count % frame_interval == 0:
                frames.append(frame)
            frame_count += 1
            
        cap.release()
        return frames
    
    def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect faces in a frame"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        return faces
    
    def analyze_face_consistency(self, frames: List[np.ndarray]) -> Dict[str, float]:
        """Analyze facial consistency across frames"""
        if len(frames) < 2:
            return {"consistency_score": 0.0, "face_count_variance": 0.0}
        
        face_counts = []
        
        for frame in frames:
            faces = self.detect_faces(frame)
            face_counts.append(len(faces))
        
        # Calculate consistency metrics
        face_count_variance = np.var(face_counts) if len(face_counts) > 1 else 0
        
        # Simple consistency score based on face count stability
        consistency_score = 1.0 / (1.0 + face_count_variance)
        
        return {
            "consistency_score": float(consistency_score),
            "face_count_variance": float(face_count_variance),
            "total_faces_detected": sum(face_counts)
        }
    
    def analyze_lighting_consistency(self, frames: List[np.ndarray]) -> Dict[str, float]:
        """Analyze lighting consistency across frames"""
        if len(frames) < 2:
            return {"lighting_variance": 0.0, "shadow_consistency": 0.0}
        
        lighting_values = []
        for frame in frames:
            # Convert to LAB color space for better lighting analysis
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            l_channel = lab[:, :, 0]
            lighting_values.append(np.mean(l_channel))
        
        lighting_variance = np.var(lighting_values) if len(lighting_values) > 1 else 0
        
        # Simple shadow consistency check
        shadow_consistency = 1.0 / (1.0 + lighting_variance / 100.0)
        
        return {
            "lighting_variance": float(lighting_variance),
            "shadow_consistency": float(shadow_consistency),
            "mean_lighting": float(np.mean(lighting_values))
        }
    
    def analyze_compression_artifacts(self, frames: List[np.ndarray]) -> Dict[str, float]:
        """Analyze compression artifacts that might indicate manipulation"""
        artifact_scores = []
        
        for frame in frames:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply high-pass filter to detect artifacts
            kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
            filtered = cv2.filter2D(gray, -1, kernel)
            
            # Calculate artifact score
            artifact_score = np.std(filtered) / 255.0
            artifact_scores.append(artifact_score)
        
        return {
            "mean_artifact_score": float(np.mean(artifact_scores)),
            "artifact_variance": float(np.var(artifact_scores)) if len(artifact_scores) > 1 else 0.0,
            "max_artifact_score": float(np.max(artifact_scores))
        }
    
    def analyze_temporal_consistency(self, frames: List[np.ndarray]) -> Dict[str, float]:
        """Analyze temporal consistency between consecutive frames"""
        if len(frames) < 2:
            return {"motion_consistency": 0.0, "temporal_variance": 0.0}
        
        motion_scores = []
        for i in range(len(frames) - 1):
            # Calculate optical flow between consecutive frames
            prev_gray = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
            curr_gray = cv2.cvtColor(frames[i + 1], cv2.COLOR_BGR2GRAY)
            
            flow = cv2.calcOpticalFlowFarneback(prev_gray, curr_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            motion_magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
            motion_scores.append(np.mean(motion_magnitude))
        
        motion_variance = np.var(motion_scores) if len(motion_scores) > 1 else 0
        motion_consistency = 1.0 / (1.0 + motion_variance / 100.0)
        
        return {
            "motion_consistency": float(motion_consistency),
            "temporal_variance": float(motion_variance),
            "mean_motion": float(np.mean(motion_scores)) if motion_scores else 0.0
        }
    
    def detect_audio_manipulation(self, audio_path: str) -> Dict[str, float]:
        """Detect audio manipulation using basic analysis"""
        try:
            # This is a simplified version - in production you'd use more sophisticated audio analysis
            # For now, return a placeholder score
            return {
                "audio_manipulation_score": 0.1,  # Low score indicates likely real
                "voice_consistency": 0.9,
                "audio_quality": 0.8
            }
        except Exception as e:
            logger.warning(f"Audio analysis failed: {e}")
            return {
                "audio_manipulation_score": 0.5,
                "voice_consistency": 0.5,
                "audio_quality": 0.5
            }
    
    def calculate_deepfake_score(self, analysis_results: Dict) -> float:
        """Calculate overall deepfake probability score"""
        # Weighted combination of different detection methods
        weights = {
            "face_consistency": 0.3,
            "lighting_consistency": 0.2,
            "compression_artifacts": 0.25,
            "temporal_consistency": 0.15,
            "audio_manipulation": 0.1
        }
        
        scores = {
            "face_consistency": analysis_results.get("face_consistency", {}).get("consistency_score", 0.5),
            "lighting_consistency": analysis_results.get("lighting_consistency", {}).get("shadow_consistency", 0.5),
            "compression_artifacts": 1.0 - analysis_results.get("compression_artifacts", {}).get("mean_artifact_score", 0.5),
            "temporal_consistency": analysis_results.get("temporal_consistency", {}).get("motion_consistency", 0.5),
            "audio_manipulation": 1.0 - analysis_results.get("audio_manipulation", {}).get("audio_manipulation_score", 0.5)
        }
        
        # Calculate weighted score (higher = more likely to be real)
        weighted_score = sum(weights[key] * scores[key] for key in weights)
        
        # Convert to deepfake probability (lower = more likely to be real)
        deepfake_probability = 1.0 - weighted_score
        
        return deepfake_probability
    
    def analyze_video(self, video_path: str, audio_path: Optional[str] = None) -> Dict:
        """Main analysis function for video deepfake detection"""
        start_time = datetime.now()
        
        try:
            # Extract frames
            frames = self.extract_frames(video_path)
            logger.info(f"Extracted {len(frames)} frames from video")
            
            # Perform various analyses
            face_analysis = self.analyze_face_consistency(frames)
            lighting_analysis = self.analyze_lighting_consistency(frames)
            compression_analysis = self.analyze_compression_artifacts(frames)
            temporal_analysis = self.analyze_temporal_consistency(frames)
            
            # Audio analysis if available
            audio_analysis = {}
            if audio_path and os.path.exists(audio_path):
                audio_analysis = self.detect_audio_manipulation(audio_path)
            
            # Combine all analysis results
            analysis_results = {
                "face_consistency": face_analysis,
                "lighting_consistency": lighting_analysis,
                "compression_artifacts": compression_analysis,
                "temporal_consistency": temporal_analysis,
                "audio_manipulation": audio_analysis
            }
            
            # Calculate overall deepfake score
            deepfake_score = self.calculate_deepfake_score(analysis_results)
            
            # Determine classification
            if deepfake_score > 0.7:
                classification = "deepfake"
            elif deepfake_score < 0.3:
                classification = "real"
            else:
                classification = "uncertain"
            
            # Calculate confidence based on consistency of indicators
            confidence = 1.0 - deepfake_score if classification == "real" else deepfake_score
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "classification": classification,
                "confidence": confidence,
                "deepfake_score": deepfake_score,
                "manipulation_indicators": analysis_results,
                "heatmap_frames": self._generate_heatmap_frames(frames, analysis_results),
                "processing_time": processing_time,
                "model_version": "1.0.0",
                "frames_analyzed": len(frames)
            }
            
        except Exception as e:
            logger.error(f"Video analysis failed: {e}")
            return {
                "classification": "error",
                "confidence": 0.0,
                "deepfake_score": 0.5,
                "manipulation_indicators": {},
                "heatmap_frames": [],
                "processing_time": 0.0,
                "model_version": "1.0.0",
                "error": str(e)
            }
    
    def _generate_heatmap_frames(self, frames: List[np.ndarray], analysis_results: Dict) -> List[float]:
        """Generate frame numbers with high manipulation probability"""
        # This is a simplified version - in production you'd create actual heatmaps
        # For now, return frame indices with higher manipulation probability
        if len(frames) == 0:
            return []
        
        # Return frames with higher artifact scores or inconsistencies
        heatmap_frames = []
        for i in range(min(10, len(frames))):
            if i % 3 == 0:  # Every 3rd frame for demonstration
                heatmap_frames.append(float(i))
        
        return heatmap_frames
