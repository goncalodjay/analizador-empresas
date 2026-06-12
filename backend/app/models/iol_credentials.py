"""IOL credentials model for encrypted credential storage."""
import uuid
from datetime import datetime, timezone
from typing import Optional

from cryptography.fernet import Fernet
from sqlalchemy import String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base
from app.core.config import settings


class IOLCredentials(Base):
    """Store encrypted IOL credentials and access token info."""

    __tablename__ = "iol_credentials"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, unique=True, index=True
    )
    iol_username: Mapped[str] = mapped_column(String(255), nullable=False)
    encrypted_password: Mapped[str] = mapped_column(Text, nullable=False)
    access_token: Mapped[str] = mapped_column(Text, nullable=False)
    token_expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    sync_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationship to User
    user: Mapped["User"] = relationship("User", back_populates="iol_credentials")

    @classmethod
    def encrypt_password(cls, raw_password: str) -> str:
        """Encrypt a password using Fernet and the configured encryption key.

        Args:
            raw_password: Plain text password to encrypt

        Returns:
            Base64-encoded encrypted password string

        Raises:
            ValueError: If encryption key is not configured
        """
        if not settings.ENCRYPTION_KEY:
            raise ValueError("ENCRYPTION_KEY not configured")

        cipher = Fernet(settings.ENCRYPTION_KEY.encode())
        encrypted = cipher.encrypt(raw_password.encode())
        return encrypted.decode()

    def decrypt_password(self) -> str:
        """Decrypt the stored encrypted password.

        Returns:
            Plain text password

        Raises:
            ValueError: If encryption key is not configured or decryption fails
        """
        if not settings.ENCRYPTION_KEY:
            raise ValueError("ENCRYPTION_KEY not configured")

        cipher = Fernet(settings.ENCRYPTION_KEY.encode())
        try:
            decrypted = cipher.decrypt(self.encrypted_password.encode())
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt password: {e}")

    def time_until_expiry(self) -> int:
        """Calculate seconds until token expiry.

        Returns:
            Seconds until expiry (negative if already expired)
        """
        # Handle both timezone-aware and naive datetimes
        expiry = self.token_expires_at
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        delta = expiry - now
        return int(delta.total_seconds())
