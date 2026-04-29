"""
Website Platforms API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.platform import WebsitePlatform
from app.models.user import User
from app.schemas.platform import WebsitePlatformCreate, WebsitePlatformResponse
from app.auth.dependencies import require_admin, get_current_active_user

router = APIRouter()


@router.get("/", response_model=List[WebsitePlatformResponse])
async def list_platforms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List all website platforms"""
    platforms = db.query(WebsitePlatform).all()
    return platforms


@router.post("/", response_model=WebsitePlatformResponse, status_code=status.HTTP_201_CREATED)
async def create_platform(
    platform_data: WebsitePlatformCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Create a new website platform (admin only)"""
    # Check if platform with this name already exists
    existing = (
        db.query(WebsitePlatform)
        .filter(WebsitePlatform.name == platform_data.name)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Platform with this name already exists",
        )

    new_platform = WebsitePlatform(**platform_data.model_dump())
    db.add(new_platform)
    db.commit()
    db.refresh(new_platform)

    return new_platform


@router.delete("/{platform_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_platform(
    platform_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Delete a website platform (admin only)"""
    platform = db.query(WebsitePlatform).filter(WebsitePlatform.id == platform_id).first()

    if platform is None:
        raise HTTPException(status_code=404, detail="Platform not found")

    db.delete(platform)
    db.commit()
