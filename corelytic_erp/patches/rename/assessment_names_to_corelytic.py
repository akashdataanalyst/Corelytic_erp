"""Module Recruitment Assessment became Corelytic Assessment on 2026-11-08, and its DocTypes got the
Corelytic prefix: Assessment Template -> Corelytic Assessment Template, Question Bank -> Corelytic
Question Bank, ... Runs before the DocTypes sync, so sync finds the renamed records. No data is
deleted (see patches/rename/utils.py). The Module Def itself and the Patch Log entries of
patches/corelytic_assessment are renamed before migrate by griderp_build/scripts/rename-db.py; this
patch also does it, for sites that migrate without that step.
"""

import frappe

from corelytic_erp.patches.rename.utils import rename_doctypes

OLD_MODULE, NEW_MODULE = "Recruitment Assessment", "Corelytic Assessment"
SUFFIXES = (
	"Answer", "Assignment Question", "Assignment", "Attempt", "Audit Log", "Notification", "Recording",
	"Result", "Section", "Settings", "Snapshot", "Template Question", "Template", "Violation",
)
DOCTYPES = {f"Assessment {s}": f"Corelytic Assessment {s}" for s in SUFFIXES}
DOCTYPES.update({"Question Bank": "Corelytic Question Bank", "Question Option": "Corelytic Question Option"})
OLD_PATCHES = "corelytic_erp.patches.recruitment_assessment."
NEW_PATCHES = "corelytic_erp.patches.corelytic_assessment."


def execute():
	if frappe.db.exists("Module Def", OLD_MODULE) and not frappe.db.exists("Module Def", NEW_MODULE):
		frappe.rename_doc("Module Def", OLD_MODULE, NEW_MODULE, force=True)
		frappe.db.set_value("Module Def", NEW_MODULE, "module_name", NEW_MODULE, update_modified=False)
	frappe.db.sql(
		"update `tabPatch Log` set patch=concat(%s, substring(patch, %s)) where patch like %s",
		(NEW_PATCHES, len(OLD_PATCHES) + 1, OLD_PATCHES + "%"),
	)

	rename_doctypes(DOCTYPES)

	# The module's old workspace and sidebar are recreated from files under the new name.
	for doctype in ("Workspace", "Sidebar"):
		if frappe.db.exists(doctype, OLD_MODULE):
			frappe.delete_doc(doctype, OLD_MODULE, force=True, ignore_permissions=True)
	frappe.clear_cache()
