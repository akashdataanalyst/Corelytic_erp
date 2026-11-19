"""Grid AI was a separate app (`grid_ai`) and is now the "Corelytic AI" module of corelytic_erp
(called the "Grid AI" module of grid_erp when this patch was written).

On a site that had grid_ai installed, this moves what the database records about the app to
corelytic_erp. No DocType, table or record is deleted: AI Settings, AI Tool Configuration,
conversations and logs stay exactly as they are.

1. Module Def "Corelytic AI" belongs to corelytic_erp.
2. grid_ai's patches that already ran are recorded under their new names, so they do not run
   again (patches/corelytic_ai/).
3. grid_ai leaves the installed apps list. `bench migrate` reads that list before any patch
   runs, so on a bench without apps/grid_ai, run
   `bench --site <site> remove-from-installed-apps grid_ai` before migrating; this step then
   finds nothing to do.

The old "Grid AI" app icon is removed by desktop.remove_old_desk_items (REMOVED_APP_ICONS).
"""

import frappe

OLD_APP = "grid_ai"
MODULE = "Corelytic AI"
RENAMED_PATCHES = {
	"grid_ai.patches.v1.move_allowed_role": "corelytic_erp.patches.corelytic_ai.move_allowed_role",
	"grid_ai.patches.v1.add_item_fields": "corelytic_erp.patches.corelytic_ai.add_item_fields",
	"grid_ai.patches.v1.user_choice_defaults": "corelytic_erp.patches.corelytic_ai.user_choice_defaults",
}


def execute():
	if frappe.db.exists("Module Def", MODULE):
		frappe.db.set_value("Module Def", MODULE, "app_name", "corelytic_erp", update_modified=False)

	for old, new in RENAMED_PATCHES.items():
		if frappe.db.exists("Patch Log", {"patch": old}) and not frappe.db.exists("Patch Log", {"patch": new}):
			frappe.db.set_value("Patch Log", {"patch": old}, "patch", new, update_modified=False)

	if OLD_APP in frappe.get_installed_apps():
		from frappe.installer import remove_from_installed_apps

		remove_from_installed_apps(OLD_APP)
