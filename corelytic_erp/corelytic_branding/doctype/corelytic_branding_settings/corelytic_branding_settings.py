import frappe
from frappe import _
from frappe.model.document import Document

from corelytic_erp.branding import (
	ensure_editor,
	extend_unlock,
	is_unlocked,
	parse_quick_actions,
	unlocked_seconds_left,
)


class CorelyticBrandingSettings(Document):
	def onload(self):
		self.set_onload("unlocked_seconds", unlocked_seconds_left())

	def validate(self):
		ensure_editor()
		if not is_unlocked():
			frappe.throw(_("Enter the branding password to edit these settings."), frappe.PermissionError)
		extend_unlock()
		self.validate_quick_actions()

	def validate_quick_actions(self):
		self.quick_actions = normalize_quick_actions(self.quick_actions)

	def on_update(self):
		# Desk boot info and rendered website pages are cached; drop them so every
		# user sees the new branding on their next page load.
		frappe.clear_cache()


def normalize_quick_actions(text):
	"""Check every DocType and rewrite it with its exact name ("leave application" ->
	"Leave Application"): the browser's permission check matches names case-sensitively."""
	actions = parse_quick_actions(text)
	if not actions:
		return text
	lines = []
	for doctype, label, hint in actions:
		row = frappe.db.get_value("DocType", doctype, ["name", "istable", "issingle"], as_dict=True)
		if not row:
			frappe.throw(_("Quick Actions: DocType {0} does not exist").format(frappe.bold(doctype)))
		if row.istable or row.issingle:
			frappe.throw(_("Quick Actions: {0} cannot be created on its own").format(frappe.bold(row.name)))
		lines.append(" | ".join(part for part in (row.name, label, hint) if part))
	return "\n".join(lines)
