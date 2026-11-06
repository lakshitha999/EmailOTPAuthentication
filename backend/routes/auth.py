"""
routes/auth.py
Flask Blueprint exposing three REST endpoints under /api:

  POST /api/send-otp      – generate & email a fresh OTP
  POST /api/verify-otp    – validate the submitted OTP
  POST /api/resend-otp    – invalidate old OTP, generate & email a new one
"""
import re
from flask import Blueprint, request, jsonify

from services.otp_service import generate_and_store_otp, verify_otp, get_attempts_left
from services.email_service import send_otp_email
from config import Config

auth_bp = Blueprint("auth", __name__, url_prefix="/api")

# Minimal RFC-5322-safe email regex
_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def _validate_email(email: str | None) -> tuple[bool, str]:
    if not email or not isinstance(email, str):
        return False, "Email address is required."
    if not _EMAIL_RE.match(email.strip()):
        return False, "Invalid email address format."
    return True, ""


# ── POST /api/send-otp ────────────────────────────────────────────────────────

@auth_bp.post("/send-otp")
def send_otp():
    """
    Body: { "email": "user@example.com" }
    Success 200: { "message": "...", "expires_in": 300 }
    Error   4xx: { "error": "..." }
    """
    data  = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()

    ok, err = _validate_email(email)
    if not ok:
        return jsonify(error=err), 400

    try:
        otp_plain, _record = generate_and_store_otp(email)
    except ValueError as exc:          # rate-limit violation
        return jsonify(error=str(exc)), 429

    try:
        send_otp_email(email, otp_plain)
    except RuntimeError as exc:
        return jsonify(error=str(exc)), 500

    return jsonify(
        message=f"A 6-digit OTP has been sent to {email}. It expires in 5 minutes.",
        expires_in=Config.OTP_EXPIRY_SECONDS,
    ), 200


# ── POST /api/verify-otp ─────────────────────────────────────────────────────

@auth_bp.post("/verify-otp")
def verify_otp_route():
    """
    Body: { "email": "user@example.com", "otp": "123456" }
    Success 200: { "message": "OTP verified successfully." }
    Error   400: { "error": "...", "attempts_left": N }
    Error   401: { "error": "..." }
    """
    data  = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    otp   = str(data.get("otp",   "")).strip()

    ok, err = _validate_email(email)
    if not ok:
        return jsonify(error=err), 400

    if not otp or not otp.isdigit() or len(otp) != 6:
        return jsonify(error="OTP must be exactly 6 digits."), 400

    success, message = verify_otp(email, otp)

    if success:
        return jsonify(message=message), 200

    attempts_left = get_attempts_left(email)
    return jsonify(error=message, attempts_left=attempts_left), 401


# ── POST /api/resend-otp ──────────────────────────────────────────────────────

@auth_bp.post("/resend-otp")
def resend_otp():
    """
    Body: { "email": "user@example.com" }
    Success 200: { "message": "...", "expires_in": 300 }
    Error   4xx: { "error": "..." }

    Internally calls generate_and_store_otp which:
      • invalidates the previous OTP
      • enforces cooldown + hourly rate limit
    """
    data  = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()

    ok, err = _validate_email(email)
    if not ok:
        return jsonify(error=err), 400

    try:
        otp_plain, _record = generate_and_store_otp(email)
    except ValueError as exc:
        return jsonify(error=str(exc)), 429

    try:
        send_otp_email(email, otp_plain)
    except RuntimeError as exc:
        return jsonify(error=str(exc)), 500

    return jsonify(
        message=f"A new OTP has been sent to {email}. It expires in 5 minutes.",
        expires_in=Config.OTP_EXPIRY_SECONDS,
    ), 200
