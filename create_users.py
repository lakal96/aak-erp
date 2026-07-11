import frappe

def run():
    """Create all AAK Agency staff user accounts with proper roles."""
    
    USERS = [
        {
            "email": "owner@aak.lk",
            "first_name": "Kapila",
            "last_name": "Perera",
            "full_name": "Kapila Perera",
            "roles": ["AAK Owner"],
            "password": "Owner@AAK2026",
            "mobile_no": "+94771234567",
        },
        {
            "email": "admin@aak.lk",
            "first_name": "Dilani",
            "last_name": "Silva",
            "full_name": "Dilani Silva",
            "roles": ["AAK Office Admin"],
            "password": "Admin@AAK2026",
            "mobile_no": "+94772345678",
        },
        {
            "email": "nimal@aak.lk",
            "first_name": "Nimal",
            "last_name": "Fernando",
            "full_name": "Nimal Fernando",
            "roles": ["AAK Sales Rep"],
            "password": "Sales@AAK2026",
            "mobile_no": "+94773456789",
            "territory": "Wattala",
        },
        {
            "email": "saman@aak.lk",
            "first_name": "Saman",
            "last_name": "Wickrama",
            "full_name": "Saman Wickrama",
            "roles": ["AAK Sales Rep"],
            "password": "Sales@AAK2026",
            "mobile_no": "+94774567890",
            "territory": "Makola",
        },
        {
            "email": "suresh@aak.lk",
            "first_name": "Suresh",
            "last_name": "Bandara",
            "full_name": "Suresh Bandara",
            "roles": ["AAK Driver"],
            "password": "Driver@AAK2026",
            "mobile_no": "+94775678901",
            "vehicle": "Van 01 - AAK",
        },
        {
            "email": "rajan@aak.lk",
            "first_name": "Rajan",
            "last_name": "Perera",
            "full_name": "Rajan Perera",
            "roles": ["AAK Cash Collector"],
            "password": "Collect@AAK2026",
            "mobile_no": "+94776789012",
        },
        {
            "email": "prasad@aak.lk",
            "first_name": "Prasad",
            "last_name": "Jayasinghe",
            "full_name": "Prasad Jayasinghe",
            "roles": ["AAK Storekeeper"],
            "password": "Store@AAK2026",
            "mobile_no": "+94777890123",
        },
    ]

    frappe.set_user("Administrator")
    
    for u in USERS:
        if frappe.db.exists("User", u["email"]):
            print(f"User already exists: {u['email']}")
            continue

        user = frappe.new_doc("User")
        user.email = u["email"]
        user.first_name = u["first_name"]
        user.last_name = u["last_name"]
        user.full_name = u["full_name"]
        user.send_welcome_email = 0
        user.mobile_no = u.get("mobile_no", "")
        user.user_type = "System User"
        
        for role_name in u["roles"]:
            user.append("roles", {"role": role_name})
        
        user.insert(ignore_permissions=True)
        
        # Set password
        from frappe.utils.password import update_password
        update_password(u["email"], u["password"])
        
        print(f"Created: {u['email']} ({u['roles'][0]})")

    # Create Sales Reps in CRM if not exists
    _create_sales_reps()

    frappe.db.commit()
    print("All users created successfully.")


def _create_sales_reps():
    reps = [
        {"sales_person_name": "Nimal Fernando", "territory": "Wattala", "employee": None},
        {"sales_person_name": "Saman Wickrama",  "territory": "Makola",  "employee": None},
        {"sales_person_name": "Dilani Silva",    "territory": None,      "employee": None},
    ]
    
    for rep in reps:
        if not frappe.db.exists("Sales Person", rep["sales_person_name"]):
            sp = frappe.new_doc("Sales Person")
            sp.sales_person_name = rep["sales_person_name"]
            sp.parent_sales_person = "Sales Team"
            sp.enabled = 1
            try:
                sp.insert(ignore_permissions=True)
                print(f"Created Sales Person: {rep['sales_person_name']}")
            except Exception as e:
                print(f"Could not create Sales Person {rep['sales_person_name']}: {e}")
