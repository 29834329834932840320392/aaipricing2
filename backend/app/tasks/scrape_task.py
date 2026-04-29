"""
Celery tasks for background scraping
"""
from celery import Task
from datetime import datetime
from sqlalchemy.orm import Session
from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.models.dealer import Dealer, Competitor
from app.models.scrape_job import ScrapeJob, ScrapeJobStatus
from app.models.vehicle import Vehicle
from app.scrapers import PlatformRouter
from app.scrapers.ai_extractor import AIVehicleExtractor
from app.config import settings
import logging
import asyncio

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """Base task with database session"""

    _db: Session = None

    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()


@celery_app.task(base=DatabaseTask, bind=True)
def scrape_dealer_task(self, dealer_id: int, job_id: int):
    """
    Background task to scrape a dealer's inventory

    Args:
        dealer_id: ID of the dealer to scrape
        job_id: ID of the ScrapeJob to update
    """
    logger.info(f"Starting scrape task for dealer {dealer_id}, job {job_id}")

    # Get database session
    db = self.db

    # Get job
    job = db.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()
    if not job:
        logger.error(f"Job {job_id} not found")
        return

    # Update job status
    job.status = ScrapeJobStatus.RUNNING
    job.started_at = datetime.utcnow()
    db.commit()

    try:
        # Get dealer
        dealer = db.query(Dealer).filter(Dealer.id == dealer_id).first()
        if not dealer:
            raise Exception(f"Dealer {dealer_id} not found")

        # Get platform name
        platform_name = dealer.platform.name

        # Create scraper
        scraper = PlatformRouter.create_scraper(
            platform_name=platform_name,
            url=dealer.url,
            headless=settings.PLAYWRIGHT_HEADLESS,
            timeout=settings.SCRAPE_TIMEOUT_SECONDS * 1000,
        )

        if not scraper:
            raise Exception(f"No scraper available for platform: {platform_name}")

        # Run scraping (async)
        vehicles = asyncio.run(_scrape_with_ai(scraper, db, settings.SCRAPE_VDP_LIMIT))

        # Update job progress
        job.total_vdps = len(vehicles)
        job.processed_vdps = len(vehicles)
        job.successful_vdps = len(vehicles)

        # Save vehicles to database
        for vehicle_data in vehicles:
            vehicle = Vehicle(
                dealer_id=dealer_id,
                vin=vehicle_data.vin,
                year=vehicle_data.year,
                make=vehicle_data.make,
                model=vehicle_data.model,
                trim=vehicle_data.trim,
                msrp=vehicle_data.msrp,
                sale_price=vehicle_data.sale_price,
                vdp_url=vehicle_data.vdp_url,
                scrape_job_id=job_id,
            )
            db.add(vehicle)

        # Update dealer last_scraped
        dealer.last_scraped_at = datetime.utcnow()

        # Complete job
        job.status = ScrapeJobStatus.COMPLETED
        job.completed_at = datetime.utcnow()

        db.commit()

        logger.info(f"Scrape task completed for dealer {dealer_id}: {len(vehicles)} vehicles")

    except Exception as e:
        logger.error(f"Scrape task failed for dealer {dealer_id}: {e}")

        job.status = ScrapeJobStatus.FAILED
        job.error_message = str(e)
        job.completed_at = datetime.utcnow()
        db.commit()

        raise


@celery_app.task(base=DatabaseTask, bind=True)
def scrape_competitor_task(self, competitor_id: int, job_id: int):
    """
    Background task to scrape a competitor's inventory

    Args:
        competitor_id: ID of the competitor to scrape
        job_id: ID of the ScrapeJob to update
    """
    logger.info(f"Starting scrape task for competitor {competitor_id}, job {job_id}")

    db = self.db

    job = db.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()
    if not job:
        logger.error(f"Job {job_id} not found")
        return

    job.status = ScrapeJobStatus.RUNNING
    job.started_at = datetime.utcnow()
    db.commit()

    try:
        competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()
        if not competitor:
            raise Exception(f"Competitor {competitor_id} not found")

        platform_name = competitor.platform.name

        scraper = PlatformRouter.create_scraper(
            platform_name=platform_name,
            url=competitor.url,
            headless=settings.PLAYWRIGHT_HEADLESS,
            timeout=settings.SCRAPE_TIMEOUT_SECONDS * 1000,
        )

        if not scraper:
            raise Exception(f"No scraper available for platform: {platform_name}")

        vehicles = asyncio.run(_scrape_with_ai(scraper, db, settings.SCRAPE_VDP_LIMIT))

        job.total_vdps = len(vehicles)
        job.processed_vdps = len(vehicles)
        job.successful_vdps = len(vehicles)

        for vehicle_data in vehicles:
            vehicle = Vehicle(
                competitor_id=competitor_id,
                vin=vehicle_data.vin,
                year=vehicle_data.year,
                make=vehicle_data.make,
                model=vehicle_data.model,
                trim=vehicle_data.trim,
                msrp=vehicle_data.msrp,
                sale_price=vehicle_data.sale_price,
                vdp_url=vehicle_data.vdp_url,
                scrape_job_id=job_id,
            )
            db.add(vehicle)

        competitor.last_scraped_at = datetime.utcnow()
        job.status = ScrapeJobStatus.COMPLETED
        job.completed_at = datetime.utcnow()

        db.commit()

        logger.info(f"Scrape task completed for competitor {competitor_id}: {len(vehicles)} vehicles")

    except Exception as e:
        logger.error(f"Scrape task failed for competitor {competitor_id}: {e}")

        job.status = ScrapeJobStatus.FAILED
        job.error_message = str(e)
        job.completed_at = datetime.utcnow()
        db.commit()

        raise


async def _scrape_with_ai(scraper, db: Session, limit: int):
    """
    Helper function to scrape and enhance with AI

    Args:
        scraper: Platform scraper instance
        db: Database session
        limit: VDP limit

    Returns:
        List of AI-enhanced ScrapedVehicle objects
    """
    # Initialize AI extractor
    ai_extractor = AIVehicleExtractor(db)

    async with scraper:
        # Scrape all VDPs
        raw_vehicles = await scraper.scrape_all(limit=limit)

        # Enhance each vehicle with AI
        enhanced_vehicles = []
        for vehicle in raw_vehicles:
            enhanced = await ai_extractor.enhance_vehicle_data(vehicle)
            enhanced_vehicles.append(enhanced)

        return enhanced_vehicles
