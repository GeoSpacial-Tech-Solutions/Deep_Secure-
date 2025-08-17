from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None

class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

# Video schemas
class VideoBase(BaseModel):
    region: str

class VideoCreate(VideoBase):
    pass

class Video(VideoBase):
    id: int
    tracking_id: str
    filename: str
    file_path: str
    file_size: Optional[int] = None
    duration: Optional[float] = None
    user_id: Optional[int] = None
    uploaded_at: datetime
    status: str

    class Config:
        from_attributes = True

# Analysis schemas
class AnalysisResultBase(BaseModel):
    classification: str
    confidence: float

class AnalysisResultCreate(AnalysisResultBase):
    video_id: int
    deepfake_score: Optional[float] = None
    manipulation_indicators: Optional[Dict[str, Any]] = None
    heatmap_frames: Optional[List[float]] = None
    processing_time: Optional[float] = None
    model_version: Optional[str] = None

class AnalysisResult(AnalysisResultBase):
    id: int
    video_id: int
    deepfake_score: Optional[float] = None
    manipulation_indicators: Optional[Dict[str, Any]] = None
    heatmap_frames: Optional[List[float]] = None
    processing_time: Optional[float] = None
    model_version: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Geospatial schemas
class GeospatialDataBase(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    timestamp: Optional[datetime] = None
    location_accuracy: Optional[float] = None
    gps_metadata: Optional[Dict[str, Any]] = None

class GeospatialDataCreate(GeospatialDataBase):
    video_id: int

class GeospatialData(GeospatialDataBase):
    id: int
    video_id: int
    location_verification: str
    verification_confidence: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Complete video with analysis
class VideoWithAnalysis(Video):
    analysis: Optional[AnalysisResult] = None
    geospatial_data: Optional[GeospatialData] = None

# Upload response
class UploadResponse(BaseModel):
    tracking_id: str
    region: str
    user_id: Optional[str] = None
    filename: str
    message: str

# Analysis request
class AnalysisRequest(BaseModel):
    video_id: str

# Analysis response
class AnalysisResponse(BaseModel):
    tracking_id: str
    classification: str
    confidence: float
    deepfake_score: Optional[float] = None
    manipulation_indicators: Optional[Dict[str, Any]] = None
    heatmap_frames: Optional[List[float]] = None
    processing_time: float
    model_version: str
    geospatial_verification: Optional[str] = None
    geospatial_confidence: Optional[float] = None

# Dashboard response
class DashboardResponse(BaseModel):
    total_videos: int
    processed_videos: int
    deepfake_count: int
    real_count: int
    uncertain_count: int
    recent_analyses: List[AnalysisResponse]
    geospatial_suspicious: int
