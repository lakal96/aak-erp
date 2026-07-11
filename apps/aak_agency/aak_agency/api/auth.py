"""
aak_agency.api.auth
────────────────────
Phone-number OTP authentication for the AAK mobile app.

Flow:
  1. Mobile calls send_otp(phone)
     → generates 6-digit OTP, stores in Frappe cache (5 min TTL)
     → sends SMS via notify.lk
  2. Mobile calls verify_otp(phone, otp)
     → validates OTP
     → returns a Frappe API key/secret pair for the matched user
"""

import random
import frappe
from frappe import _
import requests


# ── Constants ──────────────────────────────────────────────────────────────────
OTP_TTL_SECONDS = 300   # 5 minutes
OTP_CACHE_PREFIX = "aak_otp:"
NOTIFY_API_URL = "https://app.notify.lk/api/v1/send"


# ── Helpers ────────────────────────────────────────────────────────────────────

def _cache_key(phone: str) -> str:
    return f"{OTP_CACHE_PREFIX}{phone.strip()}"


def _send_sms(phone: str, message: str) -> None:
    """Send SMS via notify.lk. Raises frappe.ValidationError on failure."""
    settings = frappe.get_doc("AAK Settings")
    if not settings.notify_api_key:
        # Allow dev environments to skip SMS
        frappe.log_error(f"[AAK Auth] SMS skipped — no API key. OTP message: {message}", "SMS Skip")
        return

    resp = requests.post(
        NOTIFY_API_URL,
        data={
            "user_id": settings.notify_user_id,
            "api_key": settings.notify_api_key,
            "sender_id": settings.notify_sender_id or "AAKAgency",
            "to": phone,
            "message": message,
        },
        timeout=10,
    )
    if resp.status_code != 200 or resp.json().get("status") != "success":
        frappe.throw(_("SMS delivery failed. Please try again."), frappe.ValidationError)


# ── Public API ─────────────────────────────────────────────────────────────────

@frappe.whitelist(allow_guest=True)
def send_otp(phone: str) -> dict:
    """
    POST /api/method/aak_agency.api.auth.send_otp
    Body: { "phone": "+94771234567" }
    Returns: { "status": "sent" }
    """
    phone = phone.strip()
    if not phone:
        frappe.throw(_("Phone number is required."), frappe.ValidationError)

    # Verify the phone belongs to a known user
    if not frappe.db.exists("User", {"mobile_no": phone}):
        # Return generic message to avoid phone enumeration
        return {"status": "sent"}

    otp = str(random.randint(100000, 999999))
    frappe.cache().set_value(_cache_key(phone), otp, expires_in_sec=OTP_TTL_SECONDS)

    message = f"Your AAK Agency login code is: {otp}. Valid for 5 minutes."
    _send_sms(phone, message)

    return {"status": "sent"}


@frappe.whitelist(allow_guest=True)
def verify_otp(phone: str, otp: str) -> dict:
    """
    POST /api/method/aak_agency.api.auth.verify_otp
    Body: { "phone": "+94771234567", "otp": "123456" }
    Returns: { "api_key": "...", "api_secret": "...", "user": { ... } }
    """
    phone = phone.strip()
    otp = otp.strip()

    cached_otp = frappe.cache().get_value(_cache_key(phone))

    if not cached_otp or cached_otp != otp:
        frappe.throw(_("Invalid or expired OTP."), frappe.AuthenticationError)

    # Invalidate OTP immediately after successful use
    frappe.cache().delete_value(_cache_key(phone))

    user = frappe.db.get_value(
        "User",
        {"mobile_no": phone},
        ["name", "full_name", "email", "mobile_no"],
        as_dict=True,
    )
    if not user:
        frappe.throw(_("User not found."), frappe.DoesNotExistError)

    # Generate or retrieve API key/secret for this user
    user_doc = frappe.get_doc("User", user["name"])
    if not user_doc.api_key:
        frappe.generate_keys(user["name"])
        user_doc.reload()

    roles = frappe.get_roles(user["name"])
    aak_role = _resolve_aak_role(roles)

    return {
        "api_key": user_doc.api_key,
        "api_secret": user_doc.get_password("api_secret"),
        "user": {
            "name": user["name"],
            "full_name": user["full_name"],
            "email": user["email"],
            "mobile_no": user["mobile_no"],
            "role": aak_role,
        },
    }


@frappe.whitelist()
def get_current_user() -> dict:
    """Return profile of the currently authenticated user."""
    user = frappe.session.user
    user_doc = frappe.get_doc("User", user)
    roles = frappe.get_roles(user)
    return {
        "name": user_doc.name,
        "full_name": user_doc.full_name,
        "email": user_doc.email,
        "mobile_no": user_doc.mobile_no,
        "role": _resolve_aak_role(roles),
    }


# ── Private helpers ────────────────────────────────────────────────────────────

def _resolve_aak_role(roles: list) -> str:
    """Return the primary AAK role for the user."""
    priority = ["AAK Manager", "AAK Sales Rep", "AAK Driver", "AAK Collector"]
    for role in priority:
        if role in roles:
            return role
    return "Unknown"
