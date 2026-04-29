"""
System-wide settings model
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class SystemSettings(Base):
    """
    System-wide settings (singleton table - should only have one row)
    """

    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True)  # Should always be 1

    # OpenAI Configuration (encrypted at rest)
    openai_api_key_encrypted = Column(Text, nullable=True)  # Fernet-encrypted
    openai_model = Column(String(100), nullable=False, default="gpt-5.4-mini-2026-03-17")

    # Future: Email configuration, notification settings, etc.
    # email_smtp_host = Column(String(255), nullable=True)
    # email_smtp_port = Column(Integer, nullable=True)
    # email_from_address = Column(String(255), nullable=True)

    # Timestamps
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<SystemSettings(model='{self.openai_model}')>"
