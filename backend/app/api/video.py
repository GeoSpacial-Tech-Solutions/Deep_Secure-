from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, List
import os
import uuid
from datetime import datetime
import shutil

from app.database import get_db
from app.auth import get_current_active_user, get_current_admin_user
from app.models import User, Video, AnalysisResult, GeospatialData
from app.schemas import (
    UploadResponse, AnalysisRequest, AnalysisResponse, 
    VideoWithAnalysis, DashboardResponse
)
from app.detection_engine import DeepfakeDetectionEngine
from app.geospatial_engine import GeospatialVerificationEngine

router = APIRouter(prefix="/video", tags=["Video"])

# Initialize engines
detection_engine = DeepfakeDetectionEngine()
geospatial_engine = GeospatialVerificationEngine()

# Ensure upload directory exists
UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=UploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    region: str = Form(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload a video for analysis"""
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith('video/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a video"
        )
    
    # Generate unique tracking ID
    tracking_id = str(uuid.uuid4())
    
    # Create upload directory for region
    region_dir = os.path.join(UPLOAD_DIR, region)
    os.makedirs(region_dir, exist_ok=True)
    
    # Save file
    file_path = os.path.join(region_dir, f"{tracking_id}.mp4")
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    # Create video record in database
    video = Video(
        tracking_id=tracking_id,
        filename=file.filename,
        file_path=file_path,
        file_size=file_size,
        region=region,
        user_id=current_user.id,
        status="uploaded"
    )
    
    db.add(video)
    db.commit()
    db.refresh(video)
    
    return UploadResponse(
        tracking_id=tracking_id,
        region=region,
        user_id=str(current_user.id),
        filename=file.filename,
        message="Video uploaded successfully"
    )

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_video(
    request: AnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Analyze a video for deepfake detection and geospatial verification"""
    
    # Get video from database
    video = db.query(Video).filter(Video.tracking_id == request.video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    # Check if user owns the video or is admin
    if video.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to analyze this video"
        )
    
    # Check if video is already analyzed
    existing_analysis = db.query(AnalysisResult).filter(AnalysisResult.video_id == video.id).first()
    if existing_analysis:
        # Return existing analysis
        return _create_analysis_response(video, existing_analysis, db)
    
    # Update video status
    video.status = "processing"
    db.commit()
    
    try:
        # Perform deepfake detection
        deepfake_analysis = detection_engine.analyze_video(video.file_path)
        
        # Perform geospatial verification
        geospatial_analysis = geospatial_engine.verify_geospatial_authenticity(video.file_path)
        
        # Create analysis result
        analysis_result = AnalysisResult(
            video_id=video.id,
            classification=deepfake_analysis["classification"],
            confidence=deepfake_analysis["confidence"],
            deepfake_score=deepfake_analysis["deepfake_score"],
            manipulation_indicators=deepfake_analysis["manipulation_indicators"],
            heatmap_frames=deepfake_analysis["heatmap_frames"],
            processing_time=deepfake_analysis["processing_time"],
            model_version=deepfake_analysis["model_version"]
        )
        
        db.add(analysis_result)
        
        # Create geospatial data
        if geospatial_analysis["verification_status"] != "failed":
            geospatial_data = GeospatialData(
                video_id=video.id,
                latitude=geospatial_analysis["gps_metadata"]["latitude"],
                longitude=geospatial_analysis["gps_metadata"]["longitude"],
                altitude=geospatial_analysis["gps_metadata"]["altitude"],
                timestamp=datetime.fromisoformat(geospatial_analysis["gps_metadata"]["timestamp"]) if geospatial_analysis["gps_metadata"]["timestamp"] else None,
                location_accuracy=geospatial_analysis["gps_metadata"]["accuracy"],
                gps_metadata=geospatial_analysis["gps_metadata"],
                location_verification=geospatial_analysis["verification_status"],
                verification_confidence=geospatial_analysis["verification_confidence"]
            )
            db.add(geospatial_data)
        
        # Update video status
        video.status = "completed"
        db.commit()
        
        return _create_analysis_response(video, analysis_result, db)
        
    except Exception as e:
        # Update video status on failure
        video.status = "failed"
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )

@router.get("/status/{tracking_id}")
async def get_video_status(
    tracking_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get the status of a video analysis"""
    
    video = db.query(Video).filter(Video.tracking_id == tracking_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    # Check authorization
    if video.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this video"
        )
    
    return {
        "tracking_id": tracking_id,
        "status": video.status,
        "uploaded_at": video.uploaded_at,
        "filename": video.filename
    }

@router.get("/analysis/{tracking_id}", response_model=VideoWithAnalysis)
async def get_video_analysis(
    tracking_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get complete video analysis results"""
    
    video = db.query(Video).filter(Video.tracking_id == tracking_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    # Check authorization
    if video.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this video"
        )
    
    # Get analysis and geospatial data
    analysis = db.query(AnalysisResult).filter(AnalysisResult.video_id == video.id).first()
    geospatial_data = db.query(GeospatialData).filter(GeospatialData.video_id == video.id).first()
    
    # Create response
    video_data = VideoWithAnalysis(
        id=video.id,
        tracking_id=video.tracking_id,
        filename=video.filename,
        file_path=video.file_path,
        file_size=video.file_size,
        duration=video.duration,
        region=video.region,
        user_id=video.user_id,
        uploaded_at=video.uploaded_at,
        status=video.status,
        analysis=analysis,
        geospatial_data=geospatial_data
    )
    
    return video_data

@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics for the current user"""
    
    # Get user's videos
    user_videos = db.query(Video).filter(Video.user_id == current_user.id).all()
    
    # Get analysis results
    video_ids = [v.id for v in user_videos]
    analyses = db.query(AnalysisResult).filter(AnalysisResult.video_id.in_(video_ids)).all()
    
    # Calculate statistics
    total_videos = len(user_videos)
    processed_videos = len([v for v in user_videos if v.status == "completed"])
    
    deepfake_count = len([a for a in analyses if a.classification == "deepfake"])
    real_count = len([a for a in analyses if a.classification == "real"])
    uncertain_count = len([a for a in analyses if a.classification == "uncertain"])
    
    # Get geospatial suspicious count
    geospatial_data = db.query(GeospatialData).filter(GeospatialData.video_id.in_(video_ids)).all()
    geospatial_suspicious = len([g for g in geospatial_data if g.location_verification == "suspicious"])
    
    # Get recent analyses
    recent_analyses = []
    for analysis in analyses[-10:]:  # Last 10 analyses
        video = next((v for v in user_videos if v.id == analysis.video_id), None)
        if video:
            recent_analyses.append(_create_analysis_response(video, analysis, db))
    
    return DashboardResponse(
        total_videos=total_videos,
        processed_videos=processed_videos,
        deepfake_count=deepfake_count,
        real_count=real_count,
        uncertain_count=uncertain_count,
        recent_analyses=recent_analyses,
        geospatial_suspicious=geospatial_suspicious
    )

@router.get("/admin/all-videos")
async def get_all_videos(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Get all videos (admin only)"""
    
    videos = db.query(Video).offset(skip).limit(limit).all()
    
    return [
        {
            "id": v.id,
            "tracking_id": v.tracking_id,
            "filename": v.filename,
            "region": v.region,
            "status": v.status,
            "uploaded_at": v.uploaded_at,
            "user_id": v.user_id
        }
        for v in videos
    ]

def _create_analysis_response(video: Video, analysis: AnalysisResult, db: Session) -> AnalysisResponse:
    """Helper function to create analysis response"""
    
    # Get geospatial data
    geospatial_data = db.query(GeospatialData).filter(GeospatialData.video_id == video.id).first()
    
    return AnalysisResponse(
        tracking_id=video.tracking_id,
        classification=analysis.classification,
        confidence=analysis.confidence,
        deepfake_score=analysis.deepfake_score,
        manipulation_indicators=analysis.manipulation_indicators,
        heatmap_frames=analysis.heatmap_frames,
        processing_time=analysis.processing_time,
        model_version=analysis.model_version,
        geospatial_verification=geospatial_data.location_verification if geospatial_data else None,
        geospatial_confidence=geospatial_data.verification_confidence if geospatial_data else None
    ) 