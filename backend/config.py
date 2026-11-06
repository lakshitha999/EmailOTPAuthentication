"""
config.py
Loads all settings from environment variables (via .env).
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # ── Flask core ──────────────────────────────────────────────────────────
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
    DEBUG: bool     = os.getenv("FLASK_ENV", "development") == "development"

    # ── Database ─────────────────────────────────────────────────────────────
    # Resolve relative sqlite:/// paths against the backend/ directory
    _raw_db: str = os.getenv("DATABASE_URL", "sqlite:///otp_auth.db")
    if _raw_db.startswith("sqlite:///") and not _raw_db.startswith("sqlite:////"):
        _db_file = _raw_db[len("sqlite:///"):]
        _base_dir = os.path.dirname(os.path.abspath(__file__))
        SQLALCHEMY_DATABASE_URI: str = f"sqlite:///{os.path.join(_base_dir, _db_file)}"
    else:
        SQLALCHEMY_DATABASE_URI: str = _raw_db
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # ── Gmail SMTP ───────────────────────────────────────────────────────────
    GMAIL_ADDRESS:      str = os.getenv("GMAIL_ADDRESS", "")
    GMAIL_APP_PASSWORD: str = os.getenv("GMAIL_APP_PASSWORD", "")
    SMTP_HOST:          str = "smtp.gmail.com"
    SMTP_PORT:          int = 587

    # ── OTP behaviour ────────────────────────────────────────────────────────
    OTP_EXPIRY_SECONDS:          int = int(os.getenv("OTP_EXPIRY_SECONDS",          300))
    OTP_MAX_VERIFY_ATTEMPTS:     int = int(os.getenv("OTP_MAX_VERIFY_ATTEMPTS",       5))
    OTP_MAX_RESEND_PER_HOUR:     int = int(os.getenv("OTP_MAX_RESEND_PER_HOUR",       5))
    OTP_RESEND_COOLDOWN_SECONDS: int = int(os.getenv("OTP_RESEND_COOLDOWN_SECONDS",  30))
