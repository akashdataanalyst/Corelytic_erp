"""Corelytic print formats: branding and helpers for the Jinja print formats in
corelytic_erp/corelytic_branding/print_format/ (Corelytic Offer Letter, Corelytic Tax Invoice, ...).

Every function here is a Jinja method (hooks.py > jinja), callable by name from a
print format, e.g. {% set b = corelytic_print_branding(doc) %}.

Branding comes from Corelytic Branding Settings: company name, tagline, footer line,
colours and logo. A blank field falls back to the DocType default, the logo to the
Company logo and then to the built-in Calco logo. The logo is embedded as a data:
URI so PDFs (wkhtmltopdf) never have to fetch it over the network."""

import base64
import mimetypes
import os
import re

import frappe
from frappe import _
from frappe.utils import flt, formatdate, getdate, money_in_words, strip_html

BRANDING_DOCTYPE = "Corelytic Branding Settings"
BUILTIN_LOGO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public", "images", "calco-logo-official.svg")
BRAND_FIELDS = (
	"company_name",
	"tagline",
	"footer_line",
	"primary_color",
	"primary_deep_color",
	"header_color",
	"text_color",
)
COLOR = re.compile(r"^#[0-9a-fA-F]{3,8}$")


# ---------------------------------------------------------------------------
# Branding + company details (header / footer of every format)
# ---------------------------------------------------------------------------


def corelytic_print_branding(doc=None):
	"""Everything the shared header and footer need, for doc's company."""
	meta = frappe.get_meta(BRANDING_DOCTYPE)
	try:
		settings = frappe.get_cached_doc(BRANDING_DOCTYPE)
	except Exception:
		settings = frappe._dict()

	b = frappe._dict()
	for field in BRAND_FIELDS:
		value = (settings.get(field) or "").strip()
		df = meta.get_field(field)
		b[field] = value or (df.default if df else "") or ""
	for field in ("primary_color", "primary_deep_color", "header_color", "text_color"):
		if not COLOR.match(b[field]):
			b[field] = meta.get_field(field).default

	company = (doc and doc.get("company")) or _default_company()
	b.company = company
	company_doc = frappe.get_cached_doc("Company", company) if company else frappe._dict()
	b.company_name = b.company_name or company_doc.get("company_name") or company or ""
	b.gstin = company_doc.get("tax_id") or ""
	b.phone = company_doc.get("phone_no") or ""
	b.email = company_doc.get("email") or ""
	b.website = company_doc.get("website") or ""

	address_name = (doc and doc.get("company_address")) or _company_address(company)
	b.address_lines = _address_lines(address_name)
	if address_name:
		address = frappe.get_cached_doc("Address", address_name)
		b.phone = b.phone or address.get("phone") or ""
		b.email = b.email or address.get("email_id") or ""

	b.logo = (
		_file_data_uri(settings.get("logo"))
		or _file_data_uri(company_doc.get("company_logo"))
		or _path_data_uri(BUILTIN_LOGO)
	)

	docstatus = doc.get("docstatus") if doc else None
	b.status_label = {0: _("DRAFT"), 2: _("CANCELLED")}.get(docstatus, "") if doc and doc.meta.is_submittable else ""
	return b


def _default_company():
	return frappe.defaults.get_user_default("Company") or frappe.db.get_single_value(
		"Global Defaults", "default_company"
	)


def _company_address(company):
	if not company:
		return None
	from erpnext.setup.doctype.company.company import get_default_company_address

	return get_default_company_address(company, sort_key="is_primary_address")


def _address_lines(address_name):
	if not address_name:
		return []
	a = frappe.get_cached_doc("Address", address_name)
	city = " - ".join(v for v in (a.city, a.pincode) if v)
	region = ", ".join(v for v in (a.state, a.country) if v)
	return [v for v in (a.address_line1, a.address_line2, city, region) if v]


def _file_data_uri(file_url):
	if not file_url:
		return None
	try:
		content = frappe.get_doc("File", {"file_url": file_url}).get_content()
	except Exception:
		return None
	if isinstance(content, str):
		content = content.encode()
	mime = mimetypes.guess_type(file_url)[0] or "image/png"
	return f"data:{mime};base64,{base64.b64encode(content).decode()}"


def _path_data_uri(path):
	with open(path, "rb") as f:
		content = f.read()
	mime = mimetypes.guess_type(path)[0] or "image/svg+xml"
	return f"data:{mime};base64,{base64.b64encode(content).decode()}"


# ---------------------------------------------------------------------------
# Item / party helpers (Quotation, Sales Invoice, Delivery Note, RFQ, PO)
# ---------------------------------------------------------------------------


def corelytic_hsn(row):
	"""HSN/SAC code: India Compliance's gst_hsn_code, else Item > Customs Tariff Number."""
	code = row.get("gst_hsn_code")
	if not code and row.get("item_code"):
		code = frappe.get_cached_value("Item", row.item_code, "customs_tariff_number")
	return code or ""


def corelytic_item_description(row):
	"""The description, unless it only repeats the item name."""
	text = strip_html(row.get("description") or "").strip()
	name = (row.get("item_name") or "").strip()
	return "" if not text or text == name else text


def corelytic_party_tax_id(doctype, name):
	"""GSTIN / Tax ID of a Customer or Supplier."""
	if not name or doctype not in ("Customer", "Supplier"):
		return ""
	return frappe.get_cached_value(doctype, name, "tax_id") or ""


def corelytic_party_name(doctype, name):
	if not name:
		return ""
	field = {"Customer": "customer_name", "Supplier": "supplier_name", "Employee": "employee_name"}.get(doctype)
	return (field and frappe.get_cached_value(doctype, name, field)) or name


def corelytic_rfq_supplier(doc):
	"""Supplier this RFQ print is for: Tools > Download PDF sets doc.vendor, else the first row."""
	supplier = doc.get("vendor") or (doc.suppliers[0].supplier if doc.get("suppliers") else None)
	if not supplier:
		return frappe._dict()
	row = next((r for r in doc.suppliers if r.supplier == supplier), frappe._dict())
	return frappe._dict(
		name=supplier,
		supplier_name=corelytic_party_name("Supplier", supplier),
		email=row.get("email_id") or "",
		tax_id=corelytic_party_tax_id("Supplier", supplier),
	)


def corelytic_company_bank(company):
	"""Company's default bank account, for payment details on invoices / quotations."""
	if not company:
		return None
	rows = frappe.get_all(
		"Bank Account",
		filters={"company": company, "is_company_account": 1, "disabled": 0},
		fields=["account_name", "bank", "bank_account_no", "branch_code", "iban"],
		order_by="is_default desc, modified desc",
		limit=1,
	)
	return rows[0] if rows else None


def corelytic_grand_total(doc):
	"""Rounded total unless rounding is disabled."""
	if doc.get("rounded_total") and not doc.get("disable_rounded_total"):
		return "rounded_total"
	return "grand_total"


def corelytic_in_words(amount, currency=None):
	return money_in_words(flt(amount), currency)


# ---------------------------------------------------------------------------
# HR helpers (offer / appointment / experience / relieving letters, salary slip)
# ---------------------------------------------------------------------------


def corelytic_long_date(value=None):
	"""08 November 2026; today when value is empty."""
	return formatdate(getdate(value), "dd MMMM yyyy")


def corelytic_month(value):
	return formatdate(getdate(value), "MMMM yyyy")


def corelytic_pronouns(gender):
	"""Pronouns from Employee > Gender; neutral when it is not Male / Female."""
	return {
		"Male": frappe._dict(subject="he", object="him", possessive="his"),
		"Female": frappe._dict(subject="she", object="her", possessive="her"),
	}.get(gender) or frappe._dict(subject="they", object="them", possessive="their")


def corelytic_person_title(salutation, name):
	"""'Mr. Ravi Kumar'; just the name when there is no salutation."""
	salutation = (salutation or "").strip()
	if salutation and salutation in ("Mr", "Ms", "Mrs", "Dr", "Prof"):
		salutation += "."
	return f"{salutation} {name}".strip()


def corelytic_department(department):
	"""Department name without the company suffix ('Production - C' -> 'Production')."""
	if not department:
		return ""
	return frappe.get_cached_value("Department", department, "department_name") or department


def corelytic_employee(employee):
	if not employee:
		return frappe._dict()
	fields = [
		"name",
		"employee_name",
		"salutation",
		"gender",
		"date_of_joining",
		"relieving_date",
		"designation",
		"department",
		"pan_number",
		"bank_name",
		"bank_ac_no",
	]
	return frappe.db.get_value("Employee", employee, fields, as_dict=True) or frappe._dict()


def corelytic_job_applicant(job_applicant):
	if not job_applicant:
		return frappe._dict()
	fields = ["applicant_name", "email_id", "phone_number", "designation"]
	return frappe.db.get_value("Job Applicant", job_applicant, fields, as_dict=True) or frappe._dict()


def corelytic_salary_rows(doc):
	"""Earnings and deductions side by side: [(earning_row|None, deduction_row|None), ...].
	Statistical components and those not included in totals are left out."""

	def visible(rows):
		return [
			r for r in rows or [] if flt(r.amount) and not r.get("statistical_component") and not r.get("do_not_include_in_total")
		]

	earnings, deductions = visible(doc.get("earnings")), visible(doc.get("deductions"))
	size = max(len(earnings), len(deductions))
	return [
		(earnings[i] if i < len(earnings) else None, deductions[i] if i < len(deductions) else None)
		for i in range(size)
	]
