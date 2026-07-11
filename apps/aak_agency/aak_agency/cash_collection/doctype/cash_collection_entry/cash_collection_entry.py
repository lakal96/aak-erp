from frappe.model.document import Document


class CashCollectionEntry(Document):
    def validate(self):
        if self.amount <= 0:
            import frappe
            frappe.throw(frappe._("Amount must be greater than zero."), frappe.ValidationError)
        if self.payment_method == "Cheque" and not self.cheque_number:
            import frappe
            frappe.throw(frappe._("Cheque number is required."), frappe.ValidationError)
