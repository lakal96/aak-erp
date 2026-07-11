"""
aak_agency.delivery_management.utils
───────────────────────────────────────
Utility jobs for Delivery Management.
Called from hooks.py scheduler_events.
"""

import frappe
from frappe.utils import today


def auto_close_trips():
    """
    Scheduled daily at 11 PM.
    Any trip still 'In Transit' at end of day is marked 'Partially Delivered'.
    This prevents trips from being stuck open overnight.
    """
    open_trips = frappe.get_all(
        "Delivery Trip",
        filters={"trip_date": today(), "status": "In Transit"},
        pluck="name",
    )
    for trip_name in open_trips:
        try:
            trip = frappe.get_doc("Delivery Trip", trip_name)
            trip.status = "Partially Delivered"
            trip.save(ignore_permissions=True)
            frappe.db.commit()
        except Exception as exc:
            frappe.log_error(str(exc), f"Auto-close trip {trip_name}")
