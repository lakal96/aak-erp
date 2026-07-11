import frappe
import secrets

frappe.set_user("Administrator")
user = frappe.get_doc("User", "Administrator")
api_key = secrets.token_hex(16)
api_secret = secrets.token_hex(16)
user.api_key = api_key
user.api_secret = api_secret
user.save(ignore_permissions=True)
frappe.db.commit()
print(f"API_KEY={api_key}")
print(f"API_SECRET={api_secret}")
