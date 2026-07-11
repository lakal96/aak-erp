"""
aak_agency.api.delivery
─────────────────────────
REST API for the Driver mobile screen.

Endpoints:
  GET  get_my_trips          → trips assigned to logged-in driver (today)
  GET  get_trip_detail       → full trip with stops
  POST update_delivery_stop  → mark a stop as delivered/returned
  POST start_trip            → change trip status to In Transit
  POST complete_trip         → mark all remaining stops and close trip
"""

import frappe
from frappe import _
from frappe.utils import today, now_datetime


# ── Trip listing ───────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_my_trips(trip_date: str = None) -> list:
    """
    GET /api/method/aak_agency.api.delivery.get_my_trips
    Query: ?trip_date=2026-07-11   (defaults to today)
    Returns list of Delivery Trips for the logged-in driver.
    """
    user = frappe.session.user
    employee = _get_employee_for_user(user)
    date = trip_date or today()

    trips = frappe.get_all(
        "Delivery Trip",
        filters={"driver": employee, "trip_date": date},
        fields=[
            "name", "trip_date", "status", "route_zone",
            "total_stops", "completed_stops", "vehicle",
        ],
        order_by="creation desc",
    )
    return trips


@frappe.whitelist()
def get_trip_detail(trip_name: str) -> dict:
    """
    GET /api/method/aak_agency.api.delivery.get_trip_detail?trip_name=DT-0001
    Returns full trip with all stops and customer details.
    """
    _assert_trip_access(trip_name)

    trip = frappe.get_doc("Delivery Trip", trip_name)
    result = trip.as_dict()

    # Enrich each stop with customer address and outstanding balance
    for stop in result.get("stops", []):
        credit = frappe.db.get_value(
            "Customer Credit Limit",
            {"customer": stop["customer"]},
            ["credit_limit", "outstanding_balance"],
            as_dict=True,
        ) or {}
        stop["credit_limit"] = credit.get("credit_limit", 0)
        stop["outstanding_balance"] = credit.get("outstanding_balance", 0)

    return result


# ── Stop updates ──────────────────────────────────────────────────────────────

@frappe.whitelist()
def update_delivery_stop(
    trip_name: str,
    stop_idx: int,
    status: str,
    payment_collected: float = 0,
    payment_method: str = "",
    cheque_number: str = "",
    notes: str = "",
) -> dict:
    """
    POST /api/method/aak_agency.api.delivery.update_delivery_stop
    Body: { trip_name, stop_idx, status, payment_collected, payment_method, ... }
    Updates a single stop within a trip.
    """
    _assert_trip_access(trip_name)

    allowed_statuses = {"Delivered", "Partial", "Returned", "Pending"}
    if status not in allowed_statuses:
        frappe.throw(_(f"Invalid status: {status}"), frappe.ValidationError)

    trip = frappe.get_doc("Delivery Trip", trip_name)
    stop = trip.stops[int(stop_idx)]

    stop.status = status
    stop.payment_collected = payment_collected
    stop.payment_method = payment_method
    stop.cheque_number = cheque_number
    stop.notes = notes
    stop.delivered_at = now_datetime()

    # Recount completed stops
    trip.completed_stops = sum(
        1 for s in trip.stops if s.status in ("Delivered", "Partial")
    )
    trip.save(ignore_permissions=False)

    return {"success": True, "completed_stops": trip.completed_stops}


@frappe.whitelist()
def start_trip(trip_name: str) -> dict:
    """POST — change Delivery Trip status to In Transit."""
    _assert_trip_access(trip_name)
    trip = frappe.get_doc("Delivery Trip", trip_name)
    if trip.status != "Draft":
        frappe.throw(_("Trip is already started or completed."), frappe.ValidationError)
    trip.status = "In Transit"
    trip.save(ignore_permissions=False)
    return {"success": True, "status": trip.status}


@frappe.whitelist()
def complete_trip(trip_name: str) -> dict:
    """POST — mark trip as Completed."""
    _assert_trip_access(trip_name)
    trip = frappe.get_doc("Delivery Trip", trip_name)
    pending = [s for s in trip.stops if s.status == "Pending"]
    if pending:
        trip.status = "Partially Delivered"
    else:
        trip.status = "Completed"
    trip.save(ignore_permissions=False)
    return {"success": True, "status": trip.status}


# ── Van loading ───────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_van_loading(trip_name: str) -> list:
    """
    GET /api/method/aak_agency.api.delivery.get_van_loading?trip_name=DT-0001
    Returns the van loading list (items loaded for this trip).
    """
    _assert_trip_access(trip_name)
    items = frappe.get_all(
        "Van Loading Item",
        filters={"parent": trip_name},
        fields=["item_code", "item_name", "qty_loaded", "qty_delivered", "qty_returned"],
    )
    return items


# ── Private helpers ────────────────────────────────────────────────────────────

def _get_employee_for_user(user: str) -> str:
    employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
    if not employee:
        frappe.throw(_("No employee record linked to this user."), frappe.DoesNotExistError)
    return employee


def _assert_trip_access(trip_name: str) -> None:
    """Ensure the current user is the driver (or a manager) for this trip."""
    user = frappe.session.user
    roles = frappe.get_roles(user)
    if "AAK Manager" in roles:
        return  # Managers see all trips

    employee = _get_employee_for_user(user)
    driver = frappe.db.get_value("Delivery Trip", trip_name, "driver")
    if driver != employee:
        frappe.throw(_("You do not have access to this trip."), frappe.PermissionError)
