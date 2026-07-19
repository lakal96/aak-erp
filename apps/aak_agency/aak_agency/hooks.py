app_name = "aak_agency"
app_title = "AAK Agency"
app_publisher = "lakal96"
app_description = "CBL Chocolate Distribution ERP — Delivery, Collections & Credit Management"
app_email = "kapila@aakagency.lk"
app_license = "MIT"
app_version = "0.1.0"

# ── Module configuration ──────────────────────────────────────────────────────
required_apps = ["frappe", "erpnext"]

# ── DocType class overrides ───────────────────────────────────────────────────
# override_doctype_class = {
#   "Sales Invoice": "aak_agency.overrides.sales_invoice.CustomSalesInvoice"
# }

# ── Scheduled jobs ────────────────────────────────────────────────────────────
scheduler_events = {
    "daily": [
        # Automatically back up to S3 at midnight
        "aak_agency.utils.backup.run_s3_backup",
        # Flag overdue customers and send alert to owner
        "aak_agency.credit_management.utils.flag_overdue_customers",
    ],
    "cron": {
        # Close un-submitted delivery trips at end of day (11 PM)
        "0 23 * * *": [
            "aak_agency.delivery_management.utils.auto_close_trips",
        ],
    },
}

# ── Doc hooks ─────────────────────────────────────────────────────────────────
doc_events = {
    "Sales Invoice": {
        "on_submit": "aak_agency.credit_management.utils.update_customer_balance",
        "on_cancel": "aak_agency.credit_management.utils.update_customer_balance",
    },
    "Payment Entry": {
        "on_submit": "aak_agency.credit_management.utils.update_customer_balance",
        "on_cancel": "aak_agency.credit_management.utils.update_customer_balance",
    },
}

# ── Fixtures — exported with bench export-fixtures ───────────────────────────
fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [["module", "=", "AAK Agency"]],
    },
    {
        "doctype": "Role",
        "filters": [["name", "in", [
            "AAK Sales Rep",
            "AAK Driver",
            "AAK Cash Collector",
            "AAK Storekeeper",
            "AAK Office Admin",
            "AAK Owner",
        ]]],
    },
]

# ── Website route rules ───────────────────────────────────────────────────────
# website_route_rules = []

# ── Jinja customisation ───────────────────────────────────────────────────────
jinja = {
    "methods": [],
    "filters": [],
}
