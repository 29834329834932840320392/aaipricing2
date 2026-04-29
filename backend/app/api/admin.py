"""
Admin Panel API routes - User Management & System Settings
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User, UserRole
from app.models.system import SystemSettings
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.system import SystemSettingsResponse, SystemSettingsUpdate
from app.auth.dependencies import require_admin
from app.auth.password import hash_password
from app.auth.encryption import encrypt_api_key, decrypt_api_key

router = APIRouter()


# User Management Routes
@router.get("/users", response_model=List[UserResponse])
async def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """List all users (admin only)"""
    users = db.query(User).all()
    return users


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Create a new user (admin only)"""
    # Check if username or email already exists
    existing_user = (
        db.query(User)
        .filter((User.username == user_data.username) | (User.email == user_data.email))
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists",
        )

    # Create new user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role=user_data.role,
        is_active=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update a user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Update fields if provided
    if user_data.email is not None:
        user.email = user_data.email
    if user_data.role is not None:
        user.role = user_data.role
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    if user_data.password is not None:
        user.password_hash = hash_password(user_data.password)

    db.commit()
    db.refresh(user)

    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Delete a user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Prevent self-deletion
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    db.delete(user)
    db.commit()


# System Settings Routes
@router.get("/settings", response_model=SystemSettingsResponse)
async def get_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get system settings (admin only)"""
    settings = db.query(SystemSettings).first()

    if settings is None:
        raise HTTPException(status_code=404, detail="System settings not found")

    # Return response with has_api_key flag instead of actual key
    return SystemSettingsResponse(
        id=settings.id,
        openai_model=settings.openai_model,
        has_api_key=settings.openai_api_key_encrypted is not None,
        updated_at=settings.updated_at,
    )


@router.put("/settings", response_model=SystemSettingsResponse)
async def update_settings(
    settings_data: SystemSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update system settings (admin only)"""
    settings = db.query(SystemSettings).first()

    if settings is None:
        raise HTTPException(status_code=404, detail="System settings not found")

    # Update fields if provided
    if settings_data.openai_model is not None:
        settings.openai_model = settings_data.openai_model

    if settings_data.openai_api_key is not None:
        # Encrypt and store the API key
        settings.openai_api_key_encrypted = encrypt_api_key(settings_data.openai_api_key)

    db.commit()
    db.refresh(settings)

    return SystemSettingsResponse(
        id=settings.id,
        openai_model=settings.openai_model,
        has_api_key=settings.openai_api_key_encrypted is not None,
        updated_at=settings.updated_at,
    )
