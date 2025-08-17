from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    videos = relationship("Video", back_populates="user")

class Video(Base):
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    tracking_id = Column(String, unique=True, index=True, nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)
    duration = Column(Float)
    region = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="uploaded")  # uploaded, processing, completed, failed
    
    user = relationship("User", back_populates="videos")
    analysis = relationship("AnalysisResult", back_populates="video", uselist=False)
    geospatial_data = relationship("GeospatialData", back_populates="video", uselist=False)

class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"))
    classification = Column(String, nullable=False)  # real, deepfake, uncertain
    confidence = Column(Float, nullable=False)
    deepfake_score = Column(Float)
    manipulation_indicators = Column(JSON)  # Store detailed analysis results
    heatmap_frames = Column(JSON)  # Frame numbers with high manipulation probability
    processing_time = Column(Float)  # Time taken for analysis
    model_version = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    video = relationship("Video", back_populates="analysis")

class GeospatialData(Base):
    __tablename__ = "geospatial_data"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"))
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Float)
    timestamp = Column(DateTime(timezone=True))
    location_accuracy = Column(Float)
    gps_metadata = Column(JSON)  # Store GPS device info, satellites, etc.
    location_verification = Column(String, default="pending")  # pending, verified, suspicious
    verification_confidence = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    video = relationship("Video", back_populates="geospatial_data")

class DetectionModel(Base):
    __tablename__ = "detection_models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    version = Column(String, nullable=False)
    model_type = Column(String, nullable=False)  # deepfake, geospatial, multimodal
    file_path = Column(String, nullable=False)
    accuracy = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
