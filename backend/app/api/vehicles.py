"""
Vehicles (Dashboard) API routes
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.models.vehicle import Vehicle
from app.models.dealer import Dealer, Competitor
from app.models.user import User
from app.schemas.vehicle import VehicleResponse, VehicleStats
from app.auth.dependencies import get_current_active_user

router = APIRouter()


@router.get("/dealer/{dealer_id}", response_model=List[VehicleResponse])
async def get_dealer_vehicles(
    dealer_id: int,
    year: Optional[int] = None,
    make: Optional[str] = None,
    model: Optional[str] = None,
    hours: int = Query(24, description="Get vehicles from last N hours"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get vehicles for a specific dealer (fresh data only)"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)

    query = db.query(Vehicle).filter(
        Vehicle.dealer_id == dealer_id,
        Vehicle.scraped_at >= cutoff_time,
    )

    # Apply filters if provided
    if year:
        query = query.filter(Vehicle.year == year)
    if make:
        query = query.filter(Vehicle.make.ilike(f"%{make}%"))
    if model:
        query = query.filter(Vehicle.model.ilike(f"%{model}%"))

    vehicles = query.all()
    return vehicles


@router.get("/competitor/{competitor_id}", response_model=List[VehicleResponse])
async def get_competitor_vehicles(
    competitor_id: int,
    year: Optional[int] = None,
    make: Optional[str] = None,
    model: Optional[str] = None,
    hours: int = Query(24, description="Get vehicles from last N hours"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get vehicles for a specific competitor (fresh data only)"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)

    query = db.query(Vehicle).filter(
        Vehicle.competitor_id == competitor_id,
        Vehicle.scraped_at >= cutoff_time,
    )

    # Apply filters
    if year:
        query = query.filter(Vehicle.year == year)
    if make:
        query = query.filter(Vehicle.make.ilike(f"%{make}%"))
    if model:
        query = query.filter(Vehicle.model.ilike(f"%{model}%"))

    vehicles = query.all()
    return vehicles


@router.get("/stats/dealer/{dealer_id}", response_model=VehicleStats)
async def get_dealer_stats(
    dealer_id: int,
    hours: int = Query(24, description="Stats from last N hours"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get vehicle statistics for a dealer"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)

    stats = (
        db.query(
            func.count(Vehicle.id).label("total_count"),
            func.avg(Vehicle.msrp).label("avg_msrp"),
            func.avg(Vehicle.sale_price).label("avg_sale_price"),
            func.min(Vehicle.sale_price).label("min_price"),
            func.max(Vehicle.sale_price).label("max_price"),
        )
        .filter(
            Vehicle.dealer_id == dealer_id,
            Vehicle.scraped_at >= cutoff_time,
        )
        .first()
    )

    return VehicleStats(
        total_count=stats.total_count or 0,
        avg_msrp=stats.avg_msrp,
        avg_sale_price=stats.avg_sale_price,
        min_price=stats.min_price,
        max_price=stats.max_price,
    )
