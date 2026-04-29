"""
Scraping API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.dealer import Dealer
from app.models.scrape_job import ScrapeJob, ScrapeJobStatus
from app.models.user import User
from app.schemas.scrape import ScrapeJobCreate, ScrapeJobResponse
from app.auth.dependencies import get_current_active_user
# TODO: Import Celery task when implemented
# from app.tasks.scrape_task import scrape_dealer_task

router = APIRouter()


@router.post("/dealer/{dealer_id}", response_model=List[ScrapeJobResponse], status_code=status.HTTP_202_ACCEPTED)
async def trigger_dealer_scrape(
    dealer_id: int,
    include_competitors: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Trigger scraping for a dealer and optionally its competitors

    Returns list of created scrape jobs (1 for dealer + up to 5 for competitors)
    """
    dealer = db.query(Dealer).filter(Dealer.id == dealer_id).first()

    if dealer is None:
        raise HTTPException(status_code=404, detail="Dealer not found")

    jobs = []

    # TODO: Implement actual Celery task triggering
    # For now, create placeholder jobs

    # Create job for dealer
    dealer_job = ScrapeJob(
        task_id=f"placeholder-dealer-{dealer_id}",
        dealer_id=dealer_id,
        status=ScrapeJobStatus.PENDING,
        triggered_by_user_id=current_user.id,
    )
    db.add(dealer_job)
    jobs.append(dealer_job)

    # Create jobs for competitors if requested
    if include_competitors:
        for competitor in dealer.competitors:
            if competitor.is_active:
                competitor_job = ScrapeJob(
                    task_id=f"placeholder-competitor-{competitor.id}",
                    competitor_id=competitor.id,
                    status=ScrapeJobStatus.PENDING,
                    triggered_by_user_id=current_user.id,
                )
                db.add(competitor_job)
                jobs.append(competitor_job)

    db.commit()

    # Refresh all jobs
    for job in jobs:
        db.refresh(job)

    return jobs


@router.get("/status/{job_id}", response_model=ScrapeJobResponse)
async def get_scrape_status(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get status of a scrape job"""
    job = db.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()

    if job is None:
        raise HTTPException(status_code=404, detail="Scrape job not found")

    return job


@router.get("/dealer/{dealer_id}/recent", response_model=List[ScrapeJobResponse])
async def get_recent_dealer_jobs(
    dealer_id: int,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get recent scrape jobs for a dealer"""
    jobs = (
        db.query(ScrapeJob)
        .filter(ScrapeJob.dealer_id == dealer_id)
        .order_by(ScrapeJob.created_at.desc())
        .limit(limit)
        .all()
    )

    return jobs
