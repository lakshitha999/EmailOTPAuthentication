"""
services/email_service.py

Sends OTP emails via Gmail SMTP (TLS on port 587).

Requirements:
  • GMAIL_ADDRESS    – your Gmail address
  • GMAIL_APP_PASSWORD – a 16-character Gmail App Password
    (Account → Security → 2-Step Verification → App Passwords)
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import current_app


# ─────────────────────────── HTML template ─────────────────────────────────────

def _build_html(otp: str, email: str, expiry_minutes: int) -> str:
    digits = "".join(
        f'<span style="'
        f'display:inline-block;width:48px;height:56px;line-height:56px;'
        f'margin:0 4px;border-radius:10px;'
        f'background:linear-gradient(135deg,#1e1b4b,#312e81);'
        f'color:#a5b4fc;font-size:28px;font-weight:700;text-align:center;'
        f'letter-spacing:0;border:1.5px solid #4f46e5;">'
        f'{ch}</span>'
        for ch in otp
    )
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>Your OTP Code</title>
</head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:'Segoe UI',system-ui,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0"
         style="background:#f1f5f9;padding:40px 16px;">
    <tr><td align="center">
      <table width="100%" style="max-width:520px;background:#ffffff;
             border-radius:20px;overflow:hidden;
             box-shadow:0 10px 40px rgba(79,70,229,.12);">

        <!-- Header -->
        <tr>
          <td style="background:linear-gradient(135deg,#4f46e5,#7c3aed);
                     padding:36px 40px;text-align:center;">
            <div style="font-size:40px;margin-bottom:10px;">🔐</div>
            <h1 style="margin:0;color:#ffffff;font-size:22px;font-weight:700;
                        letter-spacing:-0.5px;">Email Verification</h1>
            <p style="margin:8px 0 0;color:#c7d2fe;font-size:14px;">
              Secure One-Time Password
            </p>
          </td>
        </tr>

        <!-- Body -->
        <tr>
          <td style="padding:40px;">
            <p style="margin:0 0 8px;color:#1e293b;font-size:16px;font-weight:600;">
              Hello,
            </p>
            <p style="margin:0 0 28px;color:#64748b;font-size:15px;line-height:1.6;">
              We received a request to verify&nbsp;
              <strong style="color:#4f46e5;">{email}</strong>.
              Use the code below to complete your authentication.
            </p>

            <!-- OTP digits -->
            <div style="text-align:center;margin:0 0 28px;">
              <p style="margin:0 0 14px;color:#64748b;font-size:13px;
                         text-transform:uppercase;letter-spacing:1px;font-weight:600;">
                Your one-time password
              </p>
              <div style="display:inline-block;">{digits}</div>
            </div>

            <!-- Expiry notice -->
            <div style="background:#eef2ff;border:1px solid #c7d2fe;border-radius:10px;
                         padding:14px 18px;margin-bottom:28px;text-align:center;">
              <p style="margin:0;color:#4338ca;font-size:14px;font-weight:600;">
                ⏱&nbsp; This code expires in
                <strong>{expiry_minutes} minute{'s' if expiry_minutes != 1 else ''}</strong>.
              </p>
            </div>

            <!-- Warning -->
            <p style="margin:0 0 8px;color:#94a3b8;font-size:13px;line-height:1.5;">
              🔒 If you did not request this code, please ignore this email.
              Your account remains secure.
            </p>
            <p style="margin:0;color:#94a3b8;font-size:13px;">
              Never share this code with anyone — we will never ask for it.
            </p>
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="background:#f8fafc;border-top:1px solid #e2e8f0;
                     padding:20px 40px;text-align:center;">
            <p style="margin:0;color:#94a3b8;font-size:12px;">
              Email OTP Authentication System &nbsp;|&nbsp; Automated message — do not reply
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>
"""


def _build_plain(otp: str, expiry_minutes: int) -> str:
    return (
        f"Your verification code is: {otp}\n\n"
        f"This code expires in {expiry_minutes} minute(s).\n\n"
        f"If you did not request this, please ignore this email.\n"
        f"Never share this code with anyone."
    )


# ─────────────────────────── sender ────────────────────────────────────────────

def send_otp_email(to_email: str, otp: str) -> None:
    """
    Send the OTP email via Gmail SMTP.
    Raises RuntimeError on configuration or delivery failure.
    """
    sender:   str = current_app.config["GMAIL_ADDRESS"]
    password: str = current_app.config["GMAIL_APP_PASSWORD"]
    host:     str = current_app.config["SMTP_HOST"]
    port:     int = current_app.config["SMTP_PORT"]
    expiry_s: int = current_app.config["OTP_EXPIRY_SECONDS"]

    if not sender or not password:
        raise RuntimeError(
            "Gmail credentials not configured. "
            "Set GMAIL_ADDRESS and GMAIL_APP_PASSWORD in your .env file."
        )

    expiry_minutes = expiry_s // 60

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🔐 Your Verification Code: {otp}"
    msg["From"]    = f"Email OTP Auth <{sender}>"
    msg["To"]      = to_email

    msg.attach(MIMEText(_build_plain(otp, expiry_minutes), "plain"))
    msg.attach(MIMEText(_build_html(otp, to_email, expiry_minutes), "html"))

    try:
        with smtplib.SMTP(host, port, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(sender, password)
            server.sendmail(sender, to_email, msg.as_string())
    except smtplib.SMTPAuthenticationError:
        raise RuntimeError(
            "Gmail authentication failed. "
            "Make sure you are using a valid App Password "
            "(not your regular Gmail password)."
        )
    except Exception as exc:
        raise RuntimeError(f"Failed to send email: {exc}") from exc
