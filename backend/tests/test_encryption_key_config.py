"""Tests for encryption key setup and validation."""
import os
import pytest
from cryptography.fernet import Fernet
from app.core.config import Settings


def test_encryption_key_loaded_from_env():
    """Test that ENCRYPTION_KEY is loaded from environment."""
    # Generate a valid key
    valid_key = Fernet.generate_key().decode()

    os.environ["ENCRYPTION_KEY"] = valid_key
    settings = Settings()

    assert settings.ENCRYPTION_KEY == valid_key
    assert isinstance(settings.ENCRYPTION_KEY, str)


def test_encryption_key_can_encrypt_decrypt():
    """Test that the loaded encryption key works for encrypt/decrypt operations."""
    valid_key = Fernet.generate_key().decode()
    os.environ["ENCRYPTION_KEY"] = valid_key

    settings = Settings()
    cipher = Fernet(settings.ENCRYPTION_KEY.encode())

    test_message = "test password"
    encrypted = cipher.encrypt(test_message.encode())
    decrypted = cipher.decrypt(encrypted).decode()

    assert decrypted == test_message


def test_encryption_key_default_empty():
    """Test that ENCRYPTION_KEY defaults to empty string if not set."""
    # Make sure env var is not set
    if "ENCRYPTION_KEY" in os.environ:
        del os.environ["ENCRYPTION_KEY"]

    settings = Settings()
    assert settings.ENCRYPTION_KEY == ""


def test_invalid_encryption_key_detected():
    """Test that invalid encryption key is detected."""
    os.environ["ENCRYPTION_KEY"] = "not-a-valid-fernet-key"

    settings = Settings()
    cipher_key = settings.ENCRYPTION_KEY

    # Should be able to store it, but attempting to use it should fail
    with pytest.raises(Exception):
        Fernet(cipher_key.encode())


def test_encryption_key_base64_format():
    """Test that encryption key must be in base64 format (Fernet key format)."""
    valid_key = Fernet.generate_key().decode()
    os.environ["ENCRYPTION_KEY"] = valid_key

    settings = Settings()

    # Key should be base64-encoded, 44 characters
    assert len(settings.ENCRYPTION_KEY) == 44
    assert settings.ENCRYPTION_KEY.endswith("=")
