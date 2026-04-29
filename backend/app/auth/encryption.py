"""
Encryption utilities for storing sensitive data (e.g., API keys) in database
"""
from cryptography.fernet import Fernet
from app.config import settings
from typing import Optional


def get_cipher() -> Fernet:
    """Get Fernet cipher instance"""
    return Fernet(settings.ENCRYPTION_KEY.encode())


def encrypt_api_key(api_key: str) -> str:
    """
    Encrypt an API key for storage in database

    Args:
        api_key: Plain text API key

    Returns:
        Encrypted API key (base64 encoded)
    """
    cipher = get_cipher()
    encrypted = cipher.encrypt(api_key.encode())
    return encrypted.decode()


def decrypt_api_key(encrypted_key: str) -> Optional[str]:
    """
    Decrypt an API key from database

    Args:
        encrypted_key: Encrypted API key from database

    Returns:
        Decrypted API key, or None if decryption fails
    """
    try:
        cipher = get_cipher()
        decrypted = cipher.decrypt(encrypted_key.encode())
        return decrypted.decode()
    except Exception:
        return None
