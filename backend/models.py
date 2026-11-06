"""
models.py
SQLAlchemy model for OTP records.

Table: otp_records
  id            – primary key
  email         – the recipient (indexed for fast lookup)
  otp_hash      – SHA-256 hex digest of the 6-digit code (never store plaintext)
  created_at    – UTC timestamp when this OTP was issued
  expires_at    – UTC timestamp when this OTP becomes invalid
  attempts      – number of failed verification attempts so far
  is_verified   – True once a correct OTP has been accepted
  is_invalidated– True when explicitly superseded by a resend or expiry cleanup
"""
from datetime import datetime, timezone
from extensions import db


class OTPRecord(db.Model):
    __tablename__ = "otp_records"

    id             = db.Column(db.Integer,  primary_key=True)
    email          = db.Column(db.String(255), nullable=False, index=True)
    otp_hash       = db.Column(db.String(64),  nullable=False)
    created_at     = db.Column(db.DateTime,    nullable=False,
                               default=lambda: datetime.now(timezone.utc))
    expires_at     = db.Column(db.DateTime,    nullable=False)
    attempts       = db.Column(db.Integer,     nullable=False, default=0)
    is_verified    = db.Column(db.Boolean,     nullable=False, default=False)
    is_invalidated = db.Column(db.Boolean,     nullable=False, default=False)

    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) >= self.expires_at.replace(tzinfo=timezone.utc)

    def is_active(self) -> bool:
        """Active = not expired, not verified, not invalidated."""
        return not self.is_expired() and not self.is_verified and not self.is_invalidated

    def __repr__(self) -> str:
        return f"<OTPRecord id={self.id} email={self.email} verified={self.is_verified}>"
