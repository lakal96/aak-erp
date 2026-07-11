"""
aak_agency.credit_management.utils
─────────────────────────────────────
Recalculate customer outstanding/overdue balances and flag overdue accounts.
Called from:
  - doc_events on Sales Invoice and Payment Entry submit/cancel
  - Daily scheduler job
"""

import frappe
from frappe.utils import today, date_diff, getdate


def update_customer_balance(doc, method=None):
    """
    Triggered on Sales Invoice / Payment Entry submit or cancel.
    Recalculates and saves the Customer Credit Limit record.
    """
    customer = doc.get("customer") or doc.get("party")
    if not customer:
        return
    _recalculate(customer)


def flag_overdue_customers():
    """
    Daily job: recalculate all customers and log overdue ones.
    """
    customers = frappe.get_all("Customer Credit Limit", pluck="customer")
    for customer in customers:
        _recalculate(customer)


def _recalculate(customer: str):
    """Fetch all open invoices for a customer and update the credit limit record."""
    if not frappe.db.exists("Customer Credit Limit", {"customer": customer}):
        return

    open_invoices = frappe.get_all(
        "Sales Invoice",
        filters={
            "customer": customer,
            "docstatus": 1,
            "outstanding_amount": (">", 0),
        },
        fields=["outstanding_amount", "due_date"],
    )

    outstanding = sum(inv["outstanding_amount"] for inv in open_invoices)
    overdue = sum(
        inv["outstanding_amount"]
        for inv in open_invoices
        if inv["due_date"] and getdate(inv["due_date"]) < getdate(today())
    )

    last_payment = frappe.db.get_value(
        "Payment Entry",
        {
            "party_type": "Customer",
            "party": customer,
            "docstatus": 1,
        },
        "posting_date",
        order_by="posting_date desc",
    )

    frappe.db.set_value(
        "Customer Credit Limit",
        {"customer": customer},
        {
            "outstanding_balance": outstanding,
            "overdue_amount": overdue,
            "last_payment_date": last_payment,
        },
    )
