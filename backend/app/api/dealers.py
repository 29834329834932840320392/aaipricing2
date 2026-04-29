"""
Dealers and Competitors API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.dealer import Dealer, Competitor
from app.models.user import User
from app.schemas.dealer import (
    DealerCreate,
    DealerUpdate,
    DealerResponse,
    CompetitorCreate,
    CompetitorUpdate,
    CompetitorResponse,
)
from app.auth.dependencies import require_admin, get_current_active_user

router = APIRouter()


# Dealer routes
@router.get("/", response_model=List[DealerResponse])
async def list_dealers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List all Ancira dealers"""
    dealers = db.query(Dealer).all()
    return dealers


@router.post("/", response_model=DealerResponse, status_code=status.HTTP_201_CREATED)
async def create_dealer(
    dealer_data: DealerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Create a new Ancira dealer (admin only)"""
    new_dealer = Dealer(**dealer_data.model_dump())
    db.add(new_dealer)
    db.commit()
    db.refresh(new_dealer)
    return new_dealer


@router.get("/{dealer_id}", response_model=DealerResponse)
async def get_dealer(
    dealer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific dealer"""
    dealer = db.query(Dealer).filter(Dealer.id == dealer_id).first()

    if dealer is None:
        raise HTTPException(status_code=404, detail="Dealer not found")

    return dealer


@router.put("/{dealer_id}", response_model=DealerResponse)
async def update_dealer(
    dealer_id: int,
    dealer_data: DealerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update a dealer (admin only)"""
    dealer = db.query(Dealer).filter(Dealer.id == dealer_id).first()

    if dealer is None:
        raise HTTPException(status_code=404, detail="Dealer not found")

    # Update fields if provided
    update_data = dealer_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(dealer, key, value)

    db.commit()
    db.refresh(dealer)
    return dealer


@router.delete("/{dealer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dealer(
    dealer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Delete a dealer (admin only)"""
    dealer = db.query(Dealer).filter(Dealer.id == dealer_id).first()

    if dealer is None:
        raise HTTPException(status_code=404, detail="Dealer not found")

    db.delete(dealer)
    db.commit()


# Competitor routes
@router.post("/{dealer_id}/competitors", response_model=CompetitorResponse, status_code=status.HTTP_201_CREATED)
async def add_competitor(
    dealer_id: int,
    competitor_data: CompetitorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Add a competitor to a dealer (admin only, max 5 competitors)"""
    dealer = db.query(Dealer).filter(Dealer.id == dealer_id).first()

    if dealer is None:
        raise HTTPException(status_code=404, detail="Dealer not found")

    # Check competitor limit (max 5)
    competitor_count = db.query(Competitor).filter(Competitor.dealer_id == dealer_id).count()

    if competitor_count >= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 5 competitors allowed per dealer",
        )

    new_competitor = Competitor(**competitor_data.model_dump())
    db.add(new_competitor)
    db.commit()
    db.refresh(new_competitor)

    return new_competitor


@router.delete("/competitors/{competitor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_competitor(
    competitor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Delete a competitor (admin only)"""
    competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()

    if competitor is None:
        raise HTTPException(status_code=404, detail="Competitor not found")

    db.delete(competitor)
    db.commit()
