"""
AAK Agency — ERPNext Initial Configuration Script
Runs inside the frappe-bench context via: bench --site frontend execute aak_setup
"""

import frappe
from frappe import _


def run():
    frappe.set_user("Administrator")

    print("\n========================================")
    print("  AAK Agency — ERPNext Configuration")
    print("========================================\n")

    _complete_setup_wizard()
    _create_warehouse_types()
    _create_warehouses()
    _create_payment_terms()
    _create_tax_templates()
    _create_item_groups()
    _create_territories()
    _create_uom()
    _create_roles()

    frappe.db.commit()
    print("\n✅ AAK Agency configuration complete!")
    print("   Open http://localhost:8080 | Login: Administrator / admin\n")


# ─── 1. COMPANY SETUP ───────────────────────────────────────────────────────

def _complete_setup_wizard():
    print("→ Setting up AAK Agency company...")

    # Mark setup as complete so the wizard screen is bypassed
    if not frappe.db.get_single_value("System Settings", "setup_complete"):
        ss = frappe.get_doc("System Settings")
        ss.language = "en"
        ss.time_zone = "Asia/Colombo"
        ss.setup_complete = 1
        ss.save(ignore_permissions=True)
        frappe.db.commit()
        print("  ✅ System settings updated.")

    # Create the company if it doesn't exist
    if frappe.db.exists("Company", "AAK Agency"):
        print("  Company 'AAK Agency' already exists — skipping.")
        return

    company = frappe.new_doc("Company")
    company.company_name = "AAK Agency"
    company.abbr = "AAK"
    company.country = "Sri Lanka"
    company.default_currency = "LKR"
    company.chart_of_accounts = "Standard"
    company.domain = "Distribution"
    company.insert(ignore_permissions=True)
    frappe.db.commit()
    print("  ✅ Company 'AAK Agency' created.")

    # Set global defaults
    gd = frappe.get_doc("Global Defaults")
    gd.default_company = "AAK Agency"
    gd.default_currency = "LKR"
    gd.country = "Sri Lanka"
    gd.save(ignore_permissions=True)
    frappe.db.commit()
    print("  ✅ Global defaults set.")


# ─── 2. WAREHOUSE TYPES ─────────────────────────────────────────────────────

def _create_warehouse_types():
    print("→ Ensuring warehouse types exist...")
    for wt in ["Stores", "Transit", "Virtual"]:
        if not frappe.db.exists("Warehouse Type", wt):
            doc = frappe.new_doc("Warehouse Type")
            doc.name = wt
            doc.insert(ignore_permissions=True)
            print(f"  ✅ Created warehouse type: {wt}")
        else:
            print(f"  — {wt} already exists.")
    frappe.db.commit()


# ─── 3. WAREHOUSES ───────────────────────────────────────────────────────────

def _create_warehouses():
    print("→ Creating warehouses...")

    warehouses = [
        {"warehouse_name": "AAK Main Warehouse",  "warehouse_type": "Stores",   "is_group": 0},
        {"warehouse_name": "Damaged Goods",        "warehouse_type": "Stores",   "is_group": 0},
        {"warehouse_name": "CBL Returns Staging",  "warehouse_type": "Transit",  "is_group": 0},
        {"warehouse_name": "Van 01",               "warehouse_type": "Transit",  "is_group": 0},
        {"warehouse_name": "Van 02",               "warehouse_type": "Transit",  "is_group": 0},
        {"warehouse_name": "Van 03",               "warehouse_type": "Transit",  "is_group": 0},
        {"warehouse_name": "Van 04",               "warehouse_type": "Transit",  "is_group": 0},
        {"warehouse_name": "Van 05",               "warehouse_type": "Transit",  "is_group": 0},
    ]

    company = "AAK Agency"
    for w in warehouses:
        name = f"{w['warehouse_name']} - AAK"
        if frappe.db.exists("Warehouse", name):
            print(f"  — {name} already exists, skipping.")
            continue
        doc = frappe.new_doc("Warehouse")
        doc.warehouse_name = w["warehouse_name"]
        doc.company = company
        doc.warehouse_type = w["warehouse_type"]
        doc.is_group = w["is_group"]
        doc.insert(ignore_permissions=True)
        print(f"  ✅ Created warehouse: {name}")

    frappe.db.commit()


# ─── 4. PAYMENT TERMS ────────────────────────────────────────────────────────

def _create_payment_terms():
    print("→ Creating payment terms...")

    terms = [
        {
            "payment_term_name": "21 Days Net",
            "due_date_based_on": "Day(s) after invoice date",
            "credit_days": 21,
            "description": "Standard AAK Agency credit term — payment due within 21 days of invoice",
        },
        {
            "payment_term_name": "Cash on Delivery",
            "due_date_based_on": "Day(s) after invoice date",
            "credit_days": 0,
            "description": "Immediate payment on delivery",
        },
        {
            "payment_term_name": "50% Advance + Balance 21 Days",
            "due_date_based_on": "Day(s) after invoice date",
            "credit_days": 21,
            "description": "For customers with overdue balance — 50% upfront required",
        },
    ]

    for t in terms:
        pt_name = t["payment_term_name"]

        # Create the Payment Term (reusable building block)
        if not frappe.db.exists("Payment Term", pt_name):
            pt = frappe.new_doc("Payment Term")
            pt.payment_term_name = pt_name
            pt.due_date_based_on = t["due_date_based_on"]
            pt.credit_days = t["credit_days"]
            pt.description = t["description"]
            pt.insert(ignore_permissions=True)
            print(f"  ✅ Created payment term: {pt_name}")
        else:
            print(f"  — Payment Term '{pt_name}' already exists.")

        # Create the Payment Terms Template (applied to customers/invoices)
        existing = frappe.db.get_value("Payment Terms Template", {"template_name": pt_name}, "name")
        if existing:
            print(f"  — Payment Terms Template '{pt_name}' already exists.")
            continue
        ptt = frappe.new_doc("Payment Terms Template")
        ptt.template_name = pt_name
        ptt.append("terms", {
            "payment_term": pt_name,
            "invoice_portion": 100,
            "due_date_based_on": t["due_date_based_on"],
            "credit_days": t["credit_days"],
        })
        ptt.insert(ignore_permissions=True)
        print(f"  ✅ Created payment terms template: {pt_name}")

    frappe.db.commit()


# ─── 5. TAX TEMPLATES ────────────────────────────────────────────────────────

def _create_tax_templates():
    print("→ Creating tax templates...")

    company = "AAK Agency"

    # Get output VAT account
    vat_output_account = frappe.db.get_value(
        "Account",
        {"account_name": ["like", "%VAT%"], "company": company, "account_type": "Tax"},
        "name"
    )

    if not vat_output_account:
        # Create VAT account under Duties and Taxes
        parent = frappe.db.get_value(
            "Account",
            {"account_name": "Duties and Taxes", "company": company},
            "name"
        )
        if not parent:
            parent = frappe.db.get_value(
                "Account",
                {"root_type": "Liability", "is_group": 1, "company": company},
                "name"
            )

        vat_output_account = f"VAT 18% - AAK"
        if not frappe.db.exists("Account", vat_output_account):
            acc = frappe.new_doc("Account")
            acc.account_name = "VAT 18%"
            acc.parent_account = parent
            acc.account_type = "Tax"
            acc.company = company
            acc.insert(ignore_permissions=True)
            print(f"  ✅ Created account: {vat_output_account}")

    # Sales Tax Template — VAT 18% Output
    template_name = "VAT 18% - Output"
    full_name = f"{template_name} - AAK"
    if not frappe.db.exists("Sales Taxes and Charges Template", full_name):
        st = frappe.new_doc("Sales Taxes and Charges Template")
        st.title = template_name
        st.company = company
        st.append("taxes", {
            "charge_type": "On Net Total",
            "account_head": vat_output_account,
            "description": "VAT @ 18%",
            "rate": 18,
        })
        st.insert(ignore_permissions=True)
        print(f"  ✅ Created sales tax template: {full_name}")
    else:
        print(f"  — {full_name} already exists, skipping.")

    # Purchase Tax Template — VAT 18% Input
    purchase_template_name = "VAT 18% - Input"
    purchase_full_name = f"{purchase_template_name} - AAK"
    if not frappe.db.exists("Purchase Taxes and Charges Template", purchase_full_name):
        pt = frappe.new_doc("Purchase Taxes and Charges Template")
        pt.title = purchase_template_name
        pt.company = company
        pt.append("taxes", {
            "charge_type": "On Net Total",
            "account_head": vat_output_account,
            "description": "VAT Input @ 18%",
            "rate": 18,
        })
        pt.insert(ignore_permissions=True)
        print(f"  ✅ Created purchase tax template: {purchase_full_name}")
    else:
        print(f"  — {purchase_full_name} already exists, skipping.")

    frappe.db.commit()


# ─── 6. ITEM GROUPS ──────────────────────────────────────────────────────────

def _create_item_groups():
    print("→ Creating item groups...")

    # Create root first
    if not frappe.db.exists("Item Group", "All Item Groups"):
        root = frappe.new_doc("Item Group")
        root.item_group_name = "All Item Groups"
        root.is_group = 1
        root.insert(ignore_permissions=True)
        print("  ✅ Created root: All Item Groups")

    groups = [
        {"item_group_name": "CBL Products",        "parent_item_group": "All Item Groups", "is_group": 1},
        {"item_group_name": "CBL Chocolates",       "parent_item_group": "CBL Products",    "is_group": 0},
        {"item_group_name": "CBL Biscuits",         "parent_item_group": "CBL Products",    "is_group": 0},
        {"item_group_name": "CBL Wafers",           "parent_item_group": "CBL Products",    "is_group": 0},
        {"item_group_name": "CBL Confectionery",    "parent_item_group": "CBL Products",    "is_group": 0},
        {"item_group_name": "CBL Other",            "parent_item_group": "CBL Products",    "is_group": 0},
    ]

    for g in groups:
        if frappe.db.exists("Item Group", g["item_group_name"]):
            print(f"  — {g['item_group_name']} already exists, skipping.")
            continue
        doc = frappe.new_doc("Item Group")
        doc.item_group_name = g["item_group_name"]
        doc.parent_item_group = g["parent_item_group"]
        doc.is_group = g["is_group"]
        doc.insert(ignore_permissions=True)
        print(f"  ✅ Created item group: {g['item_group_name']}")

    frappe.db.commit()


# ─── 7. TERRITORIES ──────────────────────────────────────────────────────────

def _create_territories():
    print("→ Creating delivery territories (routes)...")

    territories = [
        "Wattala Route",
        "Makola Route",
        "Malwana Route",
        "Kadana Route",
        "Hadala Route",
        "Mahabage Route",
        "Gongithota Route",
        "Kohalvila Route",
        "Sapugaskanda Route",
    ]

    # Ensure root + parent territory exist
    if not frappe.db.exists("Territory", "All Territories"):
        root = frappe.new_doc("Territory")
        root.territory_name = "All Territories"
        root.is_group = 1
        root.insert(ignore_permissions=True)
        print("  ✅ Created root: All Territories")

    if not frappe.db.exists("Territory", "Sri Lanka"):
        parent = frappe.new_doc("Territory")
        parent.territory_name = "Sri Lanka"
        parent.parent_territory = "All Territories"
        parent.is_group = 1
        parent.insert(ignore_permissions=True)
        print("  ✅ Created territory: Sri Lanka")

    for t in territories:
        if frappe.db.exists("Territory", t):
            print(f"  — {t} already exists, skipping.")
            continue
        doc = frappe.new_doc("Territory")
        doc.territory_name = t
        doc.parent_territory = "Sri Lanka"
        doc.is_group = 0
        doc.insert(ignore_permissions=True)
        print(f"  ✅ Created territory: {t}")

    frappe.db.commit()


# ─── 8. UNITS OF MEASURE ─────────────────────────────────────────────────────

def _create_uom():
    print("→ Creating units of measure...")

    uoms = ["Carton", "Box", "Piece", "Dozen", "Pack"]

    for u in uoms:
        if frappe.db.exists("UOM", u):
            print(f"  — {u} already exists, skipping.")
            continue
        doc = frappe.new_doc("UOM")
        doc.uom_name = u
        doc.insert(ignore_permissions=True)
        print(f"  ✅ Created UOM: {u}")

    frappe.db.commit()


# ─── 9. ROLES ────────────────────────────────────────────────────────────────

def _create_roles():
    print("→ Creating AAK custom roles...")

    roles = [
        {"role_name": "AAK Sales Rep",       "desk_access": 1},
        {"role_name": "AAK Driver",          "desk_access": 0},
        {"role_name": "AAK Cash Collector",  "desk_access": 1},
        {"role_name": "AAK Storekeeper",     "desk_access": 1},
        {"role_name": "AAK Office Admin",    "desk_access": 1},
        {"role_name": "AAK Owner",           "desk_access": 1},
    ]

    for r in roles:
        if frappe.db.exists("Role", r["role_name"]):
            print(f"  — {r['role_name']} already exists, skipping.")
            continue
        doc = frappe.new_doc("Role")
        doc.role_name = r["role_name"]
        doc.desk_access = r["desk_access"]
        doc.insert(ignore_permissions=True)
        print(f"  ✅ Created role: {r['role_name']}")

    frappe.db.commit()
