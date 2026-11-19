"""DocTypes, Roles, Print Formats and the interview dashboard page were named "Grid …" until
2026-11-08 and are "Corelytic …" now (Grid Interview Video Session -> Corelytic Interview Video
Session, Grid Branding Settings -> Corelytic Branding Settings, Grid Tax Invoice -> Corelytic Tax
Invoice, ...). Runs before the DocTypes sync, so sync finds the renamed records.

No data is deleted. frappe.rename_doc("DocType") renames the table (Singles rows for Single
DocTypes) and updates every Link / Dynamic Link / child table / permission that points to the
DocType; renaming a Role updates every user and permission row that has it.
"""

import os
import shutil

import frappe

INTERVIEW = (
	"Access Session", "Analysis", "Analysis Finding", "Audit Log", "Consent", "Notification Log",
	"Participant Event", "Portal Profile", "Processing Job", "Recording", "Reference", "Result",
	"Settings", "Transcript", "Transcript Segment", "Video Session",
)
DOCTYPES = {f"Grid Interview {n}": f"Corelytic Interview {n}" for n in INTERVIEW}
DOCTYPES["Grid Branding Settings"] = "Corelytic Branding Settings"
ROLES = {f"Grid Interview {n}": f"Corelytic Interview {n}" for n in ("Administrator", "HR User", "Reviewer", "Candidate")}
PRINT_FORMATS = {
	f"Grid {n}": f"Corelytic {n}"
	for n in (
		"Offer Letter", "Appointment Letter", "Salary Slip", "Experience Letter", "Relieving Letter", "Quotation",
		"Tax Invoice", "Delivery Note", "Request for Quotation", "Purchase Order", "Payment Receipt",
	)
}
OLD_PAGES = {"grid-interview-dashboard": "corelytic-interview-dashboard"}  # recreated from files by the sync
# (table, doctype column, document-name column) of references that can point to a Single
SINGLE_REFERENCES = (
	("Version", "ref_doctype", "docname"),
	("Comment", "reference_doctype", "reference_name"),
	("Communication", "reference_doctype", "reference_name"),
	("File", "attached_to_doctype", "attached_to_name"),
	("ToDo", "reference_type", "reference_name"),
	("Activity Log", "reference_doctype", "reference_name"),
	("Error Log", "reference_doctype", "reference_name"),
	("DocShare", "share_doctype", "share_name"),
	("Corelytic Interview Audit Log", "reference_doctype", "reference_name"),
)
FOLDERS = {"grid_interview_recordings": "corelytic_interview_recordings", "grid_interview_ingest": "corelytic_interview_ingest"}


def execute():
	for old, new in DOCTYPES.items():
		if frappe.db.exists("DocType", old) and not frappe.db.exists("DocType", new):
			frappe.rename_doc("DocType", old, new, force=True)
		# Corelytic AI keeps one AI Tool Configuration per DocType, named after it.
		if frappe.db.exists("AI Tool Configuration", old) and not frappe.db.exists("AI Tool Configuration", new):
			frappe.rename_doc("AI Tool Configuration", old, new, force=True)
	if frappe.db.table_exists("AI Tool Configuration"):
		frappe.db.sql("update `tabAI Tool Configuration` set label=replace(label, 'Grid Interview', 'Corelytic Interview') where label like 'Grid Interview%%'")
	if frappe.db.table_exists("AI Query Log"):  # Data field, not a Link
		for old, new in DOCTYPES.items():
			frappe.db.sql("update `tabAI Query Log` set reference_doctype=%s where reference_doctype=%s", (new, old))
	for old, new in DOCTYPES.items():  # list / report view settings
		frappe.db.sql("update `__UserSettings` set doctype=%s where doctype=%s", (new, old))
		# Password fields (e.g. Jitsi app secret, S3 key) are stored by DocType and document name.
		frappe.db.sql("update `__Auth` set name=%s where doctype=%s and name=%s", (new, old, old))
		frappe.db.sql("update `__Auth` set doctype=%s where doctype=%s", (new, old))

	# A Single DocType's only document is named like the DocType. rename_doc updated the
	# DocType column of these references; the document name column still has the old name.
	for old, new in DOCTYPES.items():
		if not frappe.db.get_value("DocType", new, "issingle"):
			continue
		for table, dt_col, name_col in SINGLE_REFERENCES:
			if frappe.db.table_exists(table):
				frappe.db.sql(
					f"update `tab{table}` set `{name_col}`=%s where `{dt_col}`=%s and `{name_col}`=%s", (new, new, old)
				)

	# Object-storage prefix: only rename it while recordings are not kept in S3 (nothing stored under it).
	settings = "Corelytic Interview Settings"
	if frappe.db.get_single_value(settings, "storage_backend") != "S3" and frappe.db.get_single_value(settings, "s3_prefix") == "grid-interview/":
		frappe.db.set_single_value(settings, "s3_prefix", "corelytic-interview/")

	for old, new in ROLES.items():
		if frappe.db.exists("Role", old) and not frappe.db.exists("Role", new):
			frappe.rename_doc("Role", old, new, force=True)

	for old, new in PRINT_FORMATS.items():
		if frappe.db.exists("Print Format", old) and not frappe.db.exists("Print Format", new):
			frappe.rename_doc("Print Format", old, new, force=True)
		frappe.db.sql(
			"update `tabProperty Setter` set value=%s where property='default_print_format' and value=%s", (new, old)
		)

	for page, new_page in OLD_PAGES.items():
		frappe.db.sql("delete from `tabHas Role` where parenttype='Page' and parent=%s", page)
		frappe.db.sql("delete from `tabPage` where name=%s", page)
		frappe.db.sql("update `tabSidebar Item` set link_to=%s where link_to=%s", (new_page, page))

	for old, new in FOLDERS.items():
		src, dst = frappe.get_site_path("private", old), frappe.get_site_path("private", new)
		if os.path.isdir(src) and not os.path.exists(dst):
			shutil.move(src, dst)

	frappe.clear_cache()
