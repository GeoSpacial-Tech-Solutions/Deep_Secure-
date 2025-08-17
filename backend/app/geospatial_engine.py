import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
import json
import logging
from datetime import datetime
import math
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class GPSMetadata:
    """GPS metadata structure"""
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    timestamp: Optional[datetime] = None
    accuracy: Optional[float] = None
    satellites: Optional[int] = None
    device_info: Optional[str] = None

class GeospatialVerificationEngine:
    """Engine for verifying geospatial authenticity of videos"""
    
    def __init__(self):
        self.suspicious_patterns = [
            "gps_jump",           # Sudden large location changes
            "timestamp_mismatch",  # GPS timestamp vs video timestamp mismatch
            "accuracy_anomaly",    # Unusually high GPS accuracy
            "satellite_anomaly",   # Unusual satellite count
            "speed_anomaly",       # Impossible movement speeds
            "altitude_anomaly"     # Impossible altitude changes
        ]
    
    def extract_gps_metadata(self, video_path: str) -> Optional[GPSMetadata]:
        """Extract GPS metadata from video file"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            # Try to get GPS metadata from video properties
            # This is a simplified version - in production you'd use proper EXIF extraction
            # For now, we'll simulate GPS data extraction
            
            # Get video duration and frame count
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            
            cap.release()
            
            # Simulate GPS data (in production, extract from actual video metadata)
            # This would come from video EXIF data or embedded GPS information
            gps_data = GPSMetadata(
                latitude=37.7749,  # San Francisco coordinates as example
                longitude=-122.4194,
                altitude=10.0,
                timestamp=datetime.now(),
                accuracy=5.0,  # 5 meters accuracy
                satellites=8,
                device_info="iPhone 12"
            )
            
            return gps_data
            
        except Exception as e:
            logger.error(f"Failed to extract GPS metadata: {e}")
            return None
    
    def verify_location_consistency(self, gps_data: GPSMetadata, video_path: str) -> Dict[str, float]:
        """Verify consistency of location data with video content"""
        try:
            # Analyze video frames for location consistency
            frames = self._extract_sample_frames(video_path, max_frames=20)
            
            # Check for location-specific visual elements
            location_indicators = self._analyze_location_indicators(frames)
            
            # Calculate consistency score
            consistency_score = self._calculate_location_consistency(location_indicators)
            
            return {
                "consistency_score": consistency_score,
                "location_indicators": location_indicators,
                "verification_method": "visual_analysis"
            }
            
        except Exception as e:
            logger.error(f"Location consistency verification failed: {e}")
            return {
                "consistency_score": 0.5,
                "location_indicators": {},
                "verification_method": "error",
                "error": str(e)
            }
    
    def detect_gps_manipulation(self, gps_data: GPSMetadata) -> Dict[str, float]:
        """Detect potential GPS manipulation patterns"""
        manipulation_scores = {}
        
        # Check for GPS jumps (sudden large location changes)
        # This would require historical GPS data - simplified for demo
        manipulation_scores["gps_jump"] = 0.1  # Low score = likely real
        
        # Check timestamp consistency
        if gps_data.timestamp:
            time_diff = abs((datetime.now() - gps_data.timestamp).total_seconds())
            if time_diff > 86400:  # More than 24 hours
                manipulation_scores["timestamp_mismatch"] = 0.8
            else:
                manipulation_scores["timestamp_mismatch"] = 0.1
        else:
            manipulation_scores["timestamp_mismatch"] = 0.5
        
        # Check GPS accuracy anomalies
        if gps_data.accuracy:
            if gps_data.accuracy < 1.0:  # Suspiciously high accuracy
                manipulation_scores["accuracy_anomaly"] = 0.7
            elif gps_data.accuracy > 50.0:  # Very low accuracy
                manipulation_scores["accuracy_anomaly"] = 0.6
            else:
                manipulation_scores["accuracy_anomaly"] = 0.1
        else:
            manipulation_scores["accuracy_anomaly"] = 0.5
        
        # Check satellite count anomalies
        if gps_data.satellites:
            if gps_data.satellites < 4:  # Too few satellites
                manipulation_scores["satellite_anomaly"] = 0.8
            elif gps_data.satellites > 12:  # Suspiciously many satellites
                manipulation_scores["satellite_anomaly"] = 0.6
            else:
                manipulation_scores["satellite_anomaly"] = 0.1
        else:
            manipulation_scores["satellite_anomaly"] = 0.5
        
        # Calculate overall manipulation probability
        total_score = sum(manipulation_scores.values())
        avg_score = total_score / len(manipulation_scores)
        
        return {
            "manipulation_scores": manipulation_scores,
            "overall_manipulation_probability": avg_score,
            "suspicious_patterns": [k for k, v in manipulation_scores.items() if v > 0.5]
        }
    
    def verify_geospatial_authenticity(self, video_path: str) -> Dict:
        """Main function for geospatial authenticity verification"""
        start_time = datetime.now()
        
        try:
            # Extract GPS metadata
            gps_data = self.extract_gps_metadata(video_path)
            
            if not gps_data:
                return {
                    "verification_status": "failed",
                    "error": "No GPS metadata found",
                    "processing_time": 0.0
                }
            
            # Perform various verifications
            location_consistency = self.verify_location_consistency(gps_data, video_path)
            gps_manipulation = self.detect_gps_manipulation(gps_data)
            
            # Calculate overall verification confidence
            consistency_score = location_consistency.get("consistency_score", 0.5)
            manipulation_probability = gps_manipulation.get("overall_manipulation_probability", 0.5)
            
            # Higher consistency and lower manipulation = higher confidence
            verification_confidence = (consistency_score + (1 - manipulation_probability)) / 2
            
            # Determine verification status
            if verification_confidence > 0.7:
                verification_status = "verified"
            elif verification_confidence < 0.3:
                verification_status = "suspicious"
            else:
                verification_status = "uncertain"
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "verification_status": verification_status,
                "verification_confidence": verification_confidence,
                "gps_metadata": {
                    "latitude": gps_data.latitude,
                    "longitude": gps_data.longitude,
                    "altitude": gps_data.altitude,
                    "timestamp": gps_data.timestamp.isoformat() if gps_data.timestamp else None,
                    "accuracy": gps_data.accuracy,
                    "satellites": gps_data.satellites,
                    "device_info": gps_data.device_info
                },
                "location_consistency": location_consistency,
                "gps_manipulation": gps_manipulation,
                "processing_time": processing_time,
                "verification_methods": ["gps_analysis", "visual_analysis"]
            }
            
        except Exception as e:
            logger.error(f"Geospatial verification failed: {e}")
            return {
                "verification_status": "error",
                "verification_confidence": 0.0,
                "error": str(e),
                "processing_time": 0.0
            }
    
    def _extract_sample_frames(self, video_path: str, max_frames: int = 20) -> List[np.ndarray]:
        """Extract sample frames from video for analysis"""
        frames = []
        try:
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
        except Exception as e:
            logger.error(f"Frame extraction failed: {e}")
        
        return frames
    
    def _analyze_location_indicators(self, frames: List[np.ndarray]) -> Dict[str, float]:
        """Analyze frames for location-specific visual indicators"""
        if not frames:
            return {"indicators_found": 0.0, "consistency": 0.0}
        
        # This is a simplified analysis - in production you'd use:
        # - Object recognition for landmarks
        # - Text recognition for street signs
        # - Building/architecture analysis
        # - Weather/time-of-day consistency
        
        # For now, return placeholder scores
        return {
            "indicators_found": 0.6,  # 60% of frames have location indicators
            "consistency": 0.8,       # 80% consistency across frames
            "landmark_detection": 0.7,
            "text_recognition": 0.5,
            "weather_consistency": 0.9
        }
    
    def _calculate_location_consistency(self, indicators: Dict[str, float]) -> float:
        """Calculate overall location consistency score"""
        if not indicators:
            return 0.0
        
        # Weighted average of different indicators
        weights = {
            "indicators_found": 0.3,
            "consistency": 0.4,
            "landmark_detection": 0.2,
            "text_recognition": 0.1
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for key, weight in weights.items():
            if key in indicators:
                total_score += indicators[key] * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
