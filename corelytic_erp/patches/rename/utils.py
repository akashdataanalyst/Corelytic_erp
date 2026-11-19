"""Shared steps for the 2026-11-08 rename patches (run inside `bench migrate`, pre_model_sync)."""

import frappe

# (table, doctype column, document-name column) of references that can point to a Single DocType,
# whose only document is named like the DocType itself.
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


def rename_doctypes(doctypes: dict[str, str]) -> None:
	"""Rename DocTypes old -> new, keeping all data.

	frappe.rename_doc("DocType") renames the table (Singles rows for a Single DocType) and updates
	every Link / Dynamic Link / child table / permission that points to the DocType. This adds what
	it does not cover: stored passwords, references to Single documents, Corelytic AI records and
	list view settings."""
	for old, new in doctypes.items():
		if frappe.db.exists("DocType", old) and not frappe.db.exists("DocType", new):
			frappe.rename_doc("DocType", old, new, force=True)
		# Corelytic AI keeps one AI Tool Configuration per DocType, named after it.
		if frappe.db.exists("AI Tool Configuration", old) and not frappe.db.exists("AI Tool Configuration", new):
			frappe.rename_doc("AI Tool Configuration", old, new, force=True)
			frappe.db.set_value("AI Tool Configuration", new, "label", new, update_modified=False)
		if frappe.db.table_exists("AI Query Log"):  # Data field, not a Link
			frappe.db.sql("update `tabAI Query Log` set reference_doctype=%s where reference_doctype=%s", (new, old))
		frappe.db.sql("update `__UserSettings` set doctype=%s where doctype=%s", (new, old))
		# Password fields are stored by DocType (and, for a Single, document name = DocType name).
		frappe.db.sql("update `__Auth` set name=%s where doctype=%s and name=%s", (new, old, old))
		frappe.db.sql("update `__Auth` set doctype=%s where doctype=%s", (new, old))
		if frappe.db.get_value("DocType", new, "issingle"):
			for table, dt_col, name_col in SINGLE_REFERENCES:
				if frappe.db.table_exists(table):
					frappe.db.sql(
						f"update `tab{table}` set `{name_col}`=%s where `{dt_col}`=%s and `{name_col}`=%s",
						(new, new, old),
					)
