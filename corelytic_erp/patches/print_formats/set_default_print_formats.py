"""Make the Corelytic print formats the default print format of their DocTypes.

Runs once. A default that points to a site's own (non-standard) print format is
kept; one that points to a standard format (e.g. ERPNext's "Sales Invoice Classic")
or is empty is replaced. Employee has two Corelytic formats (Experience / Relieving
Letter) and keeps its default; pick them from the print format list."""

import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

DEFAULTS = {
	"Job Offer": "Corelytic Offer Letter",
	"Appointment Letter": "Corelytic Appointment Letter",
	"Salary Slip": "Corelytic Salary Slip",
	"Quotation": "Corelytic Quotation",
	"Sales Invoice": "Corelytic Tax Invoice",
	"Delivery Note": "Corelytic Delivery Note",
	"Request for Quotation": "Corelytic Request for Quotation",
	"Purchase Order": "Corelytic Purchase Order",
	"Payment Entry": "Corelytic Payment Receipt",
}


def execute():
	for doctype, print_format in DEFAULTS.items():
		if not frappe.db.exists("DocType", doctype) or not frappe.db.exists("Print Format", print_format):
			continue
		current = frappe.get_meta(doctype).default_print_format
		if current and frappe.db.get_value("Print Format", current, "standard") == "No":
			continue
		make_property_setter(doctype, None, "default_print_format", print_format, "Data", for_doctype=True)
