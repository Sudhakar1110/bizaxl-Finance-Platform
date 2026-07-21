import json
import frappe
from frappe.model.document import Document
from frappe.utils import today, now_datetime

class Lead(Document):
    def validate(self):
        self.set_full_name()
        self.validate_pan()
        self.validate_mobile()

    def before_save(self):
        self.update_dsa_stats()

    def set_full_name(self):
        if self.first_name and not self.lead_title:
            title = self.first_name
            if self.last_name:
                title += " " + self.last_name
            self.lead_title = title

    def validate_pan(self):
        if self.pan_number:
            import re
            if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', self.pan_number):
                frappe.throw("Invalid PAN Number format")

    def validate_mobile(self):
        if self.mobile_number:
            import re
            if not re.match(r'^[6-9]\d{9}$', self.mobile_number):
                frappe.throw("Invalid Mobile Number")

    def update_dsa_stats(self):
        if self.dsa_name and not self.get("__islocal"):
            pass  # Updated on save via DSA stats

    def convert_to_customer(self):
        """Convert this lead to a Bizaxl Customer"""
        customer = frappe.get_doc({
            "doctype": "Bizaxl Customer",
            "customer_name": self.lead_title,
            "customer_type": self.customer_type or "Individual",
            "mobile_number": self.mobile_number,
            "email": self.email,
            "pan_number": self.pan_number,
            "aadhaar_number": self.aadhaar_number,
            "city": self.city,
            "state": self.state,
            "onboarded_by": self.assigned_to,
            "lead_reference": self.name,
        })
        customer.insert(ignore_permissions=True)

        self.converted_to_customer = 1
        self.converted_customer = customer.name
        self.conversion_date = today()
        self.lead_status = "Converted"
        self.save(ignore_permissions=True)

        return customer.name

    def on_update(self):
        self.update_dsa_conversion_stats()

    def update_dsa_conversion_stats(self):
        if self.dsa_name and self.lead_status == "Converted":
            dsa = frappe.get_doc("DSA Master", self.dsa_name)
            lead_count = frappe.db.count("Lead", {"dsa_name": self.dsa_name})
            conversion_count = frappe.db.count("Lead", {
                "dsa_name": self.dsa_name,
                "lead_status": "Converted"
            })
            dsa.total_leads_submitted = lead_count
            dsa.total_conversions = conversion_count
            dsa.save(ignore_permissions=True)
