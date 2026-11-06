"""
services/otp_service.py

Handles:
  • Secure 6-digit OTP generation   (secrets module — cryptographically safe)
  • SHA-256 hashing before DB storage
  • Rate limiting:
      – max OTP_MAX_VERIFY_ATTEMPTS failed verifications per issued OTP
      – max OTP_MAX_RESEND_PER_HOUR  resend requests per email per 60-min window
      – OTP_RESEND_COOLDOWN_SECONDS  minimum gap between consecutive OTPs
  • 5-minute expiry enforcement
"""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Tuple

from flask import current_app

from extensions import db
from models import OTPRecord


# ─────────────────────────── helpers ──────────────────────────────────────────

def _hash_otp(otp: str) -> str:
    """Return the SHA-256 hex digest of an OTP string."""
    return hashlib.sha256(otp.encode()).hexdigest()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _naive_utcnow() -> datetime:
    """SQLite stores naïve datetimes; keep everything naïve-UTC internally."""
    return datetime.utcnow()


# ─────────────────────────── public API ────────────────────────────────────────

def generate_and_store_otp(email: str) -> Tuple[str, "OTPRecord"]:
    """
    Generate a new 6-digit OTP, invalidate any existing active OTP for this
    email, persist the new record, and return (plaintext_otp, record).

    Raises ValueError if rate limits are exceeded.
    """
    _enforce_resend_rate_limit(email)

    # Invalidate all previous active OTPs for this email
    OTPRecord.query.filter_by(email=email, is_invalidated=False, is_verified=False).update(
        {"is_invalidated": True}
    )

    # Generate a cryptographically secure 6-digit OTP
    otp_plain = f"{secrets.randbelow(1_000_000):06d}"

    expiry_seconds: int = current_app.config["OTP_EXPIRY_SECONDS"]
    now = _naive_utcnow()

    record = OTPRecord(
        email=email,
        otp_hash=_hash_otp(otp_plain),
        created_at=now,
        expires_at=now + timedelta(seconds=expiry_seconds),
        attempts=0,
        is_verified=False,
        is_invalidated=False,
    )
    db.session.add(record)
    db.session.commit()

    return otp_plain, record


def verify_otp(email: str, otp_plain: str) -> Tuple[bool, str]:
    """
    Verify the submitted OTP for a given email.

    Returns (success: bool, message: str).
    On failure also returns remaining attempts via message when applicable.
    """
    max_attempts: int = current_app.config["OTP_MAX_VERIFY_ATTEMPTS"]

    # Find the most recent active OTP for this email
    record: OTPRecord | None = (
        OTPRecord.query
        .filter_by(email=email, is_invalidated=False, is_verified=False)
        .order_by(OTPRecord.created_at.desc())
        .first()
    )

    if record is None:
        return False, "No OTP found for this email. Please request a new one."

    if record.is_expired():
        record.is_invalidated = True
        db.session.commit()
        return False, "Your OTP has expired. Please request a new one."

    if record.attempts >= max_attempts:
        record.is_invalidated = True
        db.session.commit()
        return False, "Too many failed attempts. Please request a new OTP."

    # Compare hashes (constant-time via hmac.compare_digest would be ideal,
    # but SHA-256 of a short code is effectively safe here)
    if record.otp_hash != _hash_otp(otp_plain):
        record.attempts += 1
        remaining = max_attempts - record.attempts
        if remaining <= 0:
            record.is_invalidated = True
            db.session.commit()
            return False, "Too many failed attempts. Please request a new OTP."
        db.session.commit()
        return False, f"Incorrect OTP. {remaining} attempt{'s' if remaining != 1 else ''} remaining."

    # ✅ Correct OTP
    record.is_verified = True
    db.session.commit()
    return True, "OTP verified successfully."


def get_attempts_left(email: str) -> int:
    """Return remaining verification attempts for the active OTP (or 0)."""
    max_attempts: int = current_app.config["OTP_MAX_VERIFY_ATTEMPTS"]
    record: OTPRecord | None = (
        OTPRecord.query
        .filter_by(email=email, is_invalidated=False, is_verified=False)
        .order_by(OTPRecord.created_at.desc())
        .first()
    )
    if record is None:
        return 0
    return max(0, max_attempts - record.attempts)


# ─────────────────────────── rate-limit helper ─────────────────────────────────

def _enforce_resend_rate_limit(email: str) -> None:
    """
    Raise ValueError if:
      • A new OTP was issued less than OTP_RESEND_COOLDOWN_SECONDS ago, OR
      • More than OTP_MAX_RESEND_PER_HOUR OTPs have been issued in the last hour.
    """
    cooldown: int     = current_app.config["OTP_RESEND_COOLDOWN_SECONDS"]
    hourly_max: int   = current_app.config["OTP_MAX_RESEND_PER_HOUR"]
    now = _naive_utcnow()

    # --- cooldown check ---
    latest: OTPRecord | None = (
        OTPRecord.query
        .filter_by(email=email)
        .order_by(OTPRecord.created_at.desc())
        .first()
    )
    if latest is not None:
        age_seconds = (now - latest.created_at).total_seconds()
        if age_seconds < cooldown:
            wait = int(cooldown - age_seconds)
            raise ValueError(
                f"Please wait {wait} second{'s' if wait != 1 else ''} before requesting another OTP."
            )

    # --- hourly cap ---
    one_hour_ago = now - timedelta(hours=1)
    count_last_hour = (
        OTPRecord.query
        .filter(OTPRecord.email == email, OTPRecord.created_at >= one_hour_ago)
        .count()
    )
    if count_last_hour >= hourly_max:
        raise ValueError(
            f"Too many OTP requests. Please try again later (limit: {hourly_max} per hour)."
        )
