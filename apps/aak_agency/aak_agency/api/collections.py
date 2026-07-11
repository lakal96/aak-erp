"""
aak_agency.api.collections
─────────────────────────────
REST API for the Cash Collector mobile screen.

Endpoints:
  GET  get_pending_collections → list of customers with outstanding payments
  POST submit_collection       → record cash/cheque received from a customer
  GET  get_collection_summary  → today's collection total for the logged-in collector
"""

import frappe
from frappe import _
from frappe.utils import today, now_datetime


# ── Pending collections ───────────────────────────────────────────────────────

@frappe.whitelist()
def get_pending_collections(zone: str = None) -> list:
    """
    GET /api/method/aak_agency.api.collections.get_pending_collections
    Query: ?zone=Wattala
    Returns customers with outstanding balances > 0.
    """
    filters = {"outstanding_balance": (">", 0)}
    if zone:
        # Join with Customer to filter by territory
        customers_in_zone = frappe.get_all(
            "Customer", filters={"territory": zone}, pluck="name"
        )
        filters["customer"] = ("in", customers_in_zone)

    records = frappe.get_all(
        "Customer Credit Limit",
        filters=filters,
        fields=[
            "customer", "customer_name", "outstanding_balance",
            "overdue_amount", "credit_limit", "last_payment_date",
        ],
        order_by="overdue_amount desc",
    )
    return records


# ── Submit collection ──────────────────────────────────────────────────────────

@frappe.whitelist()
def submit_collection(
    customer: str,
    amount: float,
    payment_method: str,
    cheque_number: str = "",
    cheque_date: str = "",
    bank_name: str = "",
    notes: str = "",
) -> dict:
    """
    POST /api/method/aak_agency.api.collections.submit_collection
    Body:
      {
        "customer": "CUST-001",
        "amount": 15000.00,
        "payment_method": "Cash",       # Cash | Cheque
        "cheque_number": "001234",      # if Cheque
        "cheque_date": "2026-07-15",    # if Cheque
        "bank_name": "Sampath",         # if Cheque
        "notes": ""
      }
    Creates a Cash Collection Entry and a Payment Entry in ERPNext.
    """
    amount = float(amount)
    if amount <= 0:
        frappe.throw(_("Amount must be greater than zero."), frappe.ValidationError)

    allowed_methods = {"Cash", "Cheque"}
    if payment_method not in allowed_methods:
        frappe.throw(_(f"Invalid payment method: {payment_method}"), frappe.ValidationError)

    if payment_method == "Cheque" and not cheque_number:
        frappe.throw(_("Cheque number is required for cheque payments."), frappe.ValidationError)

    # 1. Create internal Cash Collection Entry (audit trail)
    entry = frappe.new_doc("Cash Collection Entry")
    entry.customer = customer
    entry.collection_date = today()
    entry.collected_by = frappe.session.user
    entry.amount = amount
    entry.payment_method = payment_method
    entry.cheque_number = cheque_number
    entry.cheque_date = cheque_date or None
    entry.bank_name = bank_name
    entry.notes = notes
    entry.insert(ignore_permissions=False)
    entry.submit()

    # 2. Create ERPNext Payment Entry (links to Sales Invoices)
    payment = frappe.new_doc("Payment Entry")
    payment.payment_type = "Receive"
    payment.party_type = "Customer"
    payment.party = customer
    payment.paid_amount = amount
    payment.received_amount = amount
    payment.reference_no = cheque_number or entry.name
    payment.reference_date = cheque_date or today()
    payment.remarks = notes

    # Fetch default receivable account
    company = frappe.defaults.get_defaults().get("company")
    payment.company = company
    payment.paid_to = frappe.db.get_value(
        "Company", company, "default_cash_account"
    ) or frappe.db.get_value(
        "Account",
        {"account_type": "Cash", "company": company, "is_group": 0},
        "name",
    )
    payment.paid_from = frappe.db.get_value(
        "Company", company, "default_receivable_account"
    )

    payment.insert(ignore_permissions=False)
    payment.submit()

    return {
        "success": True,
        "collection_entry": entry.name,
        "payment_entry": payment.name,
    }


# ── Daily summary ─────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_collection_summary(collection_date: str = None) -> dict:
    """
    GET /api/method/aak_agency.api.collections.get_collection_summary
    Query: ?collection_date=2026-07-11
    Returns today's collection totals for the logged-in collector.
    """
    date = collection_date or today()
    user = frappe.session.user

    entries = frappe.get_all(
        "Cash Collection Entry",
        filters={
            "collection_date": date,
            "collected_by": user,
            "docstatus": 1,
        },
        fields=["customer", "amount", "payment_method", "cheque_number"],
    )

    total_cash = sum(e["amount"] for e in entries if e["payment_method"] == "Cash")
    total_cheque = sum(e["amount"] for e in entries if e["payment_method"] == "Cheque")

    return {
        "date": date,
        "entries": entries,
        "total_cash": total_cash,
        "total_cheque": total_cheque,
        "grand_total": total_cash + total_cheque,
        "entry_count": len(entries),
    }
