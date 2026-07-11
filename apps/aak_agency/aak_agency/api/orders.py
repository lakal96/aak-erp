"""
aak_agency.api.orders
───────────────────────
REST API for the Sales Rep mobile screen.

Endpoints:
  GET  get_customer_list   → paginated list of assigned customers
  GET  get_customer_detail → customer info + credit + last order
  POST create_order        → create a Sales Order (pre-sales flow)
  GET  get_my_orders       → orders submitted by logged-in rep (today / date range)
"""

import frappe
from frappe import _
from frappe.utils import today, add_days


# ── Customer listing ──────────────────────────────────────────────────────────

@frappe.whitelist()
def get_customer_list(zone: str = None, search: str = None, page: int = 1, page_size: int = 50) -> dict:
    """
    GET /api/method/aak_agency.api.orders.get_customer_list
    Query: ?zone=Wattala&search=Perera&page=1
    Returns paginated customer list optionally filtered by zone and name search.
    """
    filters = {"disabled": 0}
    if zone:
        filters["territory"] = zone
    if search:
        filters["customer_name"] = ("like", f"%{search}%")

    page = max(1, int(page))
    page_size = min(int(page_size), 100)
    start = (page - 1) * page_size

    customers = frappe.get_all(
        "Customer",
        filters=filters,
        fields=["name", "customer_name", "territory", "mobile_no", "customer_group"],
        limit_start=start,
        limit_page_length=page_size,
        order_by="customer_name asc",
    )

    total = frappe.db.count("Customer", filters=filters)

    return {
        "customers": customers,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@frappe.whitelist()
def get_customer_detail(customer: str) -> dict:
    """
    GET /api/method/aak_agency.api.orders.get_customer_detail?customer=CUST-001
    Returns customer profile, credit position and last 5 orders.
    """
    cust = frappe.get_doc("Customer", customer)

    credit = frappe.db.get_value(
        "Customer Credit Limit",
        {"customer": customer},
        ["credit_limit", "outstanding_balance", "overdue_amount", "last_payment_date"],
        as_dict=True,
    ) or {}

    last_orders = frappe.get_all(
        "Sales Order",
        filters={"customer": customer, "docstatus": 1},
        fields=["name", "transaction_date", "grand_total", "delivery_status"],
        limit_page_length=5,
        order_by="transaction_date desc",
    )

    return {
        "customer": {
            "name": cust.name,
            "customer_name": cust.customer_name,
            "territory": cust.territory,
            "mobile_no": cust.mobile_no,
        },
        "credit": credit,
        "last_orders": last_orders,
    }


# ── Order creation ────────────────────────────────────────────────────────────

@frappe.whitelist()
def create_order(customer: str, items: list, delivery_date: str = None, notes: str = "") -> dict:
    """
    POST /api/method/aak_agency.api.orders.create_order
    Body:
      {
        "customer": "CUST-001",
        "delivery_date": "2026-07-12",
        "notes": "...",
        "items": [
          {"item_code": "CBL-MUNCHEE-DARK-80G", "qty": 10, "rate": 120}
        ]
      }
    Creates and submits a Sales Order.
    """
    if not items or not isinstance(items, list):
        frappe.throw(_("At least one item is required."), frappe.ValidationError)

    # Credit check — block order if customer is overdue
    credit = frappe.db.get_value(
        "Customer Credit Limit",
        {"customer": customer},
        ["credit_limit", "outstanding_balance", "overdue_amount"],
        as_dict=True,
    )
    if credit and credit.get("overdue_amount", 0) > 0:
        frappe.throw(
            _(f"Customer has overdue balance of {credit['overdue_amount']}. Cannot place order."),
            frappe.ValidationError,
        )

    order = frappe.new_doc("Sales Order")
    order.customer = customer
    order.transaction_date = today()
    order.delivery_date = delivery_date or add_days(today(), 1)
    order.po_no = notes  # store rep notes in PO reference field

    for item in items:
        order.append("items", {
            "item_code": item["item_code"],
            "qty": item["qty"],
            "rate": item.get("rate", 0),
            "delivery_date": order.delivery_date,
        })

    order.insert(ignore_permissions=False)
    order.submit()

    return {
        "success": True,
        "order_name": order.name,
        "grand_total": order.grand_total,
    }


# ── Rep's own orders ──────────────────────────────────────────────────────────

@frappe.whitelist()
def get_my_orders(from_date: str = None, to_date: str = None) -> list:
    """
    GET /api/method/aak_agency.api.orders.get_my_orders
    Query: ?from_date=2026-07-01&to_date=2026-07-11
    Returns orders created by the logged-in sales rep.
    """
    from_date = from_date or today()
    to_date = to_date or today()

    orders = frappe.get_all(
        "Sales Order",
        filters={
            "transaction_date": ("between", [from_date, to_date]),
            "owner": frappe.session.user,
            "docstatus": 1,
        },
        fields=[
            "name", "customer", "transaction_date",
            "grand_total", "delivery_status", "delivery_date",
        ],
        order_by="transaction_date desc",
    )
    return orders
