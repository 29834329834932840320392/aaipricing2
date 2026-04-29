"""
Initialize database with default data on first run
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User, UserRole
from app.models.system import SystemSettings
from app.auth.password import hash_password
from app.config import settings
import logging

logger = logging.getLogger(__name__)


def create_initial_data():
    """Create initial admin user and system settings if they don't exist"""
    db: Session = SessionLocal()

    try:
        # Check if any users exist
        user_count = db.query(User).count()

        if user_count == 0:
            # Create initial admin user
            admin_user = User(
                username=settings.INITIAL_ADMIN_USERNAME,
                email=settings.INITIAL_ADMIN_EMAIL,
                password_hash=hash_password(settings.INITIAL_ADMIN_PASSWORD),
                role=UserRole.ADMIN,
                is_active=True,
            )
            db.add(admin_user)
            db.commit()
            logger.info(f"Created initial admin user: {settings.INITIAL_ADMIN_USERNAME}")
        else:
            logger.info(f"Users already exist ({user_count} users)")

        # Check if system settings exist
        sys_settings = db.query(SystemSettings).first()

        if sys_settings is None:
            # Create default system settings
            sys_settings = SystemSettings(
                id=1,  # Always ID 1 (singleton)
                openai_model=settings.DEFAULT_OPENAI_MODEL,
                openai_api_key_encrypted=None,  # Admin will set this
            )
            db.add(sys_settings)
            db.commit()
            logger.info("Created default system settings")
        else:
            logger.info("System settings already exist")

    except Exception as e:
        logger.error(f"Error creating initial data: {e}")
        db.rollback()
    finally:
        db.close()
