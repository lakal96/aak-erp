import frappe
from frappe.model.document import Document


class DeliveryTrip(Document):
    def before_save(self):
        self.total_stops = len(self.stops)
        self.completed_stops = sum(
            1 for s in self.stops if s.status in ("Delivered", "Partial")
        )
        self.total_cash_collected = sum(
            s.payment_collected or 0
            for s in self.stops
            if s.payment_method == "Cash"
        )

    def on_submit(self):
        if self.status == "Draft":
            frappe.throw(
                frappe._("Cannot submit a trip that has not been started."),
                frappe.ValidationError,
            )

    def on_cancel(self):
        # Reset all pending stops
        for stop in self.stops:
            if stop.status == "Pending":
                stop.status = "Pending"  # no change, just explicit
