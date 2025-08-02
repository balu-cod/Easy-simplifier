from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import aiofiles
import uuid
from datetime import datetime
import json

from database.postgresql import get_db
from database.mongodb import get_mongo_db
from models.user import User
from services.ai_service import AIService
from services.file_service import FileService
from middleware.auth import get_current_active_user
from config.settings import settings

router = APIRouter()
ai_service = AIService()
file_service = FileService()

@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    mongo_db = Depends(get_mongo_db)
):
    """Upload and process an image"""
    
    # Validate file type
    if file.content_type not in settings.ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file.content_type} not allowed. Supported types: {', '.join(settings.ALLOWED_FILE_TYPES)}"
        )
    
    # Validate file size
    file_content = await file.read()
    if len(file_content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes"
        )
    
    try:
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        filename = f"{file_id}.{file_extension}"
        
        # Save file locally first
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, filename)
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        # Process image with AI
        processing_result = await ai_service.process_image(file_content, file.content_type)
        
        # Upload to cloud storage if configured
        cloud_url = await file_service.upload_to_cloud(file_path, filename)
        
        # Save image metadata to MongoDB
        image_document = {
            "id": file_id,
            "user_id": current_user.id,
            "original_filename": file.filename,
            "filename": filename,
            "file_path": file_path,
            "cloud_url": cloud_url,
            "file_size": len(file_content),
            "content_type": file.content_type,
            "upload_date": datetime.utcnow(),
            "processing_result": processing_result,
            "is_processed": processing_result.get("success", False),
            "tags": [],
            "is_public": False
        }
        
        result = await mongo_db.images.insert_one(image_document)
        
        # Update user stats
        current_user.total_score += 10  # Award points for uploading
        db.commit()
        
        return {
            "success": True,
            "image_id": file_id,
            "filename": filename,
            "cloud_url": cloud_url,
            "processing_result": processing_result,
            "message": "Image uploaded and processed successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing image: {str(e)}"
        )

@router.get("/")
async def get_user_images(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    mongo_db = Depends(get_mongo_db)
):
    """Get user's uploaded images"""
    try:
        cursor = mongo_db.images.find(
            {"user_id": current_user.id}
        ).skip(skip).limit(limit).sort("upload_date", -1)
        
        images = []
        async for image in cursor:
            image['_id'] = str(image['_id'])
            images.append(image)
        
        total_count = await mongo_db.images.count_documents({"user_id": current_user.id})
        
        return {
            "images": images,
            "total": total_count,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching images: {str(e)}"
        )

@router.get("/{image_id}")
async def get_image(
    image_id: str,
    current_user: User = Depends(get_current_active_user),
    mongo_db = Depends(get_mongo_db)
):
    """Get specific image details"""
    try:
        image = await mongo_db.images.find_one({
            "id": image_id,
            "$or": [
                {"user_id": current_user.id},
                {"is_public": True}
            ]
        })
        
        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found"
            )
        
        image['_id'] = str(image['_id'])
        return image
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching image: {str(e)}"
        )

@router.post("/{image_id}/reprocess")
async def reprocess_image(
    image_id: str,
    current_user: User = Depends(get_current_active_user),
    mongo_db = Depends(get_mongo_db)
):
    """Reprocess an image with updated AI models"""
    try:
        image = await mongo_db.images.find_one({
            "id": image_id,
            "user_id": current_user.id
        })
        
        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found"
            )
        
        # Read the file
        file_path = image.get("file_path")
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Original file not found for reprocessing"
            )
        
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        # Reprocess with AI
        processing_result = await ai_service.process_image(file_content, image.get("content_type"))
        
        # Update database
        await mongo_db.images.update_one(
            {"id": image_id},
            {
                "$set": {
                    "processing_result": processing_result,
                    "is_processed": processing_result.get("success", False),
                    "last_processed": datetime.utcnow()
                }
            }
        )
        
        return {
            "success": True,
            "processing_result": processing_result,
            "message": "Image reprocessed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reprocessing image: {str(e)}"
        )

@router.put("/{image_id}/tags")
async def update_image_tags(
    image_id: str,
    tags: List[str],
    current_user: User = Depends(get_current_active_user),
    mongo_db = Depends(get_mongo_db)
):
    """Update image tags"""
    try:
        result = await mongo_db.images.update_one(
            {"id": image_id, "user_id": current_user.id},
            {"$set": {"tags": tags}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found"
            )
        
        return {"success": True, "message": "Tags updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating tags: {str(e)}"
        )

@router.put("/{image_id}/visibility")
async def update_image_visibility(
    image_id: str,
    is_public: bool,
    current_user: User = Depends(get_current_active_user),
    mongo_db = Depends(get_mongo_db)
):
    """Update image visibility (public/private)"""
    try:
        result = await mongo_db.images.update_one(
            {"id": image_id, "user_id": current_user.id},
            {"$set": {"is_public": is_public}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found"
            )
        
        return {
            "success": True, 
            "message": f"Image visibility updated to {'public' if is_public else 'private'}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating visibility: {str(e)}"
        )

@router.delete("/{image_id}")
async def delete_image(
    image_id: str,
    current_user: User = Depends(get_current_active_user),
    mongo_db = Depends(get_mongo_db)
):
    """Delete an image"""
    try:
        image = await mongo_db.images.find_one({
            "id": image_id,
            "user_id": current_user.id
        })
        
        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found"
            )
        
        # Delete file from local storage
        file_path = image.get("file_path")
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete from cloud storage
        if image.get("cloud_url"):
            await file_service.delete_from_cloud(image.get("filename"))
        
        # Delete from database
        await mongo_db.images.delete_one({"id": image_id})
        
        return {"success": True, "message": "Image deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting image: {str(e)}"
        )

@router.get("/public/gallery")
async def get_public_gallery(
    skip: int = 0,
    limit: int = 20,
    tags: Optional[str] = None,
    mongo_db = Depends(get_mongo_db)
):
    """Get public image gallery"""
    try:
        filter_query = {"is_public": True}
        
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            filter_query["tags"] = {"$in": tag_list}
        
        cursor = mongo_db.images.find(
            filter_query,
            {
                "processing_result.simplified_content": 0,  # Exclude large text fields
                "processing_result.extracted_text": 0
            }
        ).skip(skip).limit(limit).sort("upload_date", -1)
        
        images = []
        async for image in cursor:
            image['_id'] = str(image['_id'])
            # Remove sensitive user info
            image.pop("user_id", None)
            images.append(image)
        
        total_count = await mongo_db.images.count_documents(filter_query)
        
        return {
            "images": images,
            "total": total_count,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching public gallery: {str(e)}"
        )

@router.post("/{image_id}/analyze")
async def analyze_image_custom(
    image_id: str,
    analysis_type: str,
    current_user: User = Depends(get_current_active_user),
    mongo_db = Depends(get_mongo_db)
):
    """Perform custom analysis on an image"""
    try:
        image = await mongo_db.images.find_one({
            "id": image_id,
            "$or": [
                {"user_id": current_user.id},
                {"is_public": True}
            ]
        })
        
        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found"
            )
        
        processing_result = image.get("processing_result", {})
        
        if analysis_type == "sentiment":
            extracted_text = processing_result.get("extracted_text", "")
            sentiment = await ai_service.analyze_sentiment(extracted_text)
            return {"analysis_type": "sentiment", "result": sentiment}
        
        elif analysis_type == "summary":
            return {
                "analysis_type": "summary",
                "result": processing_result.get("summary", "No summary available")
            }
        
        elif analysis_type == "objects":
            return {
                "analysis_type": "objects",
                "result": processing_result.get("objects_detected", [])
            }
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid analysis type. Supported types: sentiment, summary, objects"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error performing analysis: {str(e)}"
        )