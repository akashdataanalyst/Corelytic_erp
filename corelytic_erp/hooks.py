from . import __version__ as app_version

app_name = "corelytic_erp"
app_title = "Corelytic ERP"
app_publisher = "Calco PolyTechnik Pvt Ltd"
app_description = "Calco PolyTechnik Manufacturing ERP - Branding, WhatsApp, Corelytic Assessment, Interviews and AI Assistant"
app_email = "mis.1@calco.in"
app_license = "Proprietary"
app_version = app_version
# Corelytic Assessment builds on Job Opening / Job Applicant from HRMS.
required_apps = ["frappe", "erpnext", "hrms"]

# This app has five modules (see modules.txt):
#   Corelytic Branding     corelytic_erp/corelytic_branding    branding, print formats
#   Corelytic WhatsApp          corelytic_erp/corelytic_whatsapp           WhatsApp messaging
#   Corelytic Assessment corelytic_erp/corelytic_assessment  online candidate assessments
#   Corelytic AI                corelytic_erp/corelytic_ai                 AI Assistant (questions on ERP data)
#   Corelytic Interview         corelytic_erp/corelytic_interview          video interviews on HRMS Interview
#
# Candidates use one portal, /candidate-portal (www/candidate-portal): their assessments,
# interviews, results, profile and references.

# ---------------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------------

# Served by corelytic_erp.assets (Python backend), not /assets, so they load on any
# setup without building assets. URLs change automatically when a file changes.
from corelytic_erp.assets import url as _asset

# Desk (logged-in) pages. calco_workspace_config.js must load before calco_branding.js.
app_include_css = [
	_asset("css/calco_branding.css"),
	_asset("css/workspace_presentation.css"),
	_asset("css/corelytic_desk_theme.css"),
]
app_include_js = [
	_asset("js/calco_workspace_config.js"),
	_asset("js/calco_branding.js"),
	_asset("js/workspace_presentation.js"),
	_asset("js/corelytic_interview/corelytic_interview.js"),
]

# Website pages, including the login page.
web_include_css = [_asset("css/calco_branding.css")]
web_include_js = [
	_asset("js/calco_workspace_config.js"),
	_asset("js/calco_branding.js"),
]

# ---------------------------------------------------------------------------
# Desk navigation (Frappe 16.51: apps screen tile + Dock + one Sidebar per module)
# ---------------------------------------------------------------------------

# /apps shows one "Corelytic ERP" tile. Its rail (dock/corelytic_erp/corelytic_erp.json) lists the modules:
# WhatsApp, Corelytic Assessment, AI Assistant, Branding. Each opens that module's Sidebar
# (<module>/sidebar/). An entry is shown only to users who may see its module (Role > Modules).
add_to_apps_screen = [
	{
		"name": "corelytic_erp",
		"logo": _asset("images/corelytic_erp.svg"),
		"title": "Corelytic ERP",
		"route": "/desk/corelytic-assessment",
		# Desk users only: candidates (Website Users) must land on /candidate-portal after login.
		"has_permission": "corelytic_erp.desktop.can_open_corelytic_erp",
	}
]

# ---------------------------------------------------------------------------
# Corelytic Branding Settings (see branding.py)
# ---------------------------------------------------------------------------

# Desk receives the settings through boot, website/login pages through <head>.
boot_session = "corelytic_erp.branding.boot_session"
update_website_context = "corelytic_erp.branding.update_website_context"
# Saving the settings runs frappe.clear_cache(), which drops every cache key except
# these prefixes; the edit unlock must survive it or each save would lock the form.
persistent_cache_keys = ["corelytic_branding_unlocked:"]

# Only the Administrator user may open the settings.
has_permission = {
	"Corelytic Branding Settings": "corelytic_erp.branding.has_permission",
	# Corelytic Interview: interviewers see only their own interviews' records.
	"Corelytic Interview Video Session": "corelytic_erp.corelytic_interview.permissions.has_interview_linked_permission",
	"Corelytic Interview Transcript": "corelytic_erp.corelytic_interview.permissions.has_interview_linked_permission",
	"Corelytic Interview Analysis": "corelytic_erp.corelytic_interview.permissions.has_interview_linked_permission",
}

# ---------------------------------------------------------------------------
# Corelytic print formats (module Corelytic Branding: corelytic_erp/corelytic_branding/print_format/, shared
# header / footer / CSS in templates/print/corelytic_print.html, helpers in printing.py).
# Logo, company name and colours come from Corelytic Branding Settings.
# ---------------------------------------------------------------------------

jinja = {
	"methods": [
		"corelytic_erp.printing.corelytic_print_branding",
		"corelytic_erp.printing.corelytic_hsn",
		"corelytic_erp.printing.corelytic_item_description",
		"corelytic_erp.printing.corelytic_party_tax_id",
		"corelytic_erp.printing.corelytic_party_name",
		"corelytic_erp.printing.corelytic_rfq_supplier",
		"corelytic_erp.printing.corelytic_company_bank",
		"corelytic_erp.printing.corelytic_grand_total",
		"corelytic_erp.printing.corelytic_in_words",
		"corelytic_erp.printing.corelytic_long_date",
		"corelytic_erp.printing.corelytic_month",
		"corelytic_erp.printing.corelytic_pronouns",
		"corelytic_erp.printing.corelytic_person_title",
		"corelytic_erp.printing.corelytic_department",
		"corelytic_erp.printing.corelytic_employee",
		"corelytic_erp.printing.corelytic_job_applicant",
		"corelytic_erp.printing.corelytic_salary_rows",
	],
}

# ---------------------------------------------------------------------------
# Corelytic WhatsApp (module corelytic_erp/corelytic_whatsapp, merged from the former
# corelytic_whatsapp app). See corelytic_whatsapp/README.md and docs/whatsapp.md.
# ---------------------------------------------------------------------------

# desktop.py removes desk icons / sidebars of older versions (Business Suite, merged apps).
# Install also creates the starter WhatsApp setup (instance, settings, templates, rules).
after_install = [
	"corelytic_erp.desktop.remove_old_desk_items",
	"corelytic_erp.corelytic_whatsapp.seed.seed_all",
	"corelytic_erp.corelytic_assessment.install.after_install",
	"corelytic_erp.corelytic_ai.install.after_install",
	"corelytic_erp.corelytic_interview.setup.install.after_install",
]
after_migrate = [
	"corelytic_erp.desktop.remove_old_desk_items",
	"corelytic_erp.corelytic_assessment.install.after_migrate",
	"corelytic_erp.corelytic_ai.install.after_migrate",
	"corelytic_erp.corelytic_interview.setup.install.after_migrate",
]
before_uninstall = "corelytic_erp.corelytic_assessment.install.before_uninstall"

before_install = "corelytic_erp.corelytic_whatsapp.install.ensure_manager_role"
before_migrate = "corelytic_erp.corelytic_whatsapp.install.ensure_manager_role"

# Every document event goes to the notification engine. It returns after one
# cached lookup when the DocType has no enabled WhatsApp Notification Rule.
_whatsapp_handler = "corelytic_erp.corelytic_whatsapp.services.notification_engine.handle_doc_event"
_assessment_sync = "corelytic_erp.corelytic_assessment.workflow.sync_job_applicant_assessment"
doc_events = {
	"*": {
		"after_insert": _whatsapp_handler,
		"on_update": _whatsapp_handler,
		"on_submit": _whatsapp_handler,
		"on_cancel": _whatsapp_handler,
		"on_change": _whatsapp_handler,
	},
	# Corelytic Assessment: keep the applicant's assessment fields in sync and
	# auto-send the assessment on Shortlist.
	"Job Applicant": {
		"after_insert": _assessment_sync,
		"on_update": _assessment_sync,
	},
	# Corelytic AI: a new DocType gets a (disabled) AI Tool Configuration.
	"DocType": {
		"after_insert": "corelytic_erp.corelytic_ai.tools.discovery.on_doctype_created",
	},
}

scheduler_events = {
	"cron": {
		# Re-queue WhatsApp messages whose retry time has come.
		"* * * * *": ["corelytic_erp.corelytic_whatsapp.services.dispatcher.process_due_retries"],
		# Corelytic Interview: reconcile Desk changes, send due reminders, sync Email Queue status / retries.
		"*/5 * * * *": ["corelytic_erp.corelytic_interview.services.scheduling.run_cycle"],
	},
	# Corelytic Assessment
	"all": [
		"corelytic_erp.corelytic_assessment.scheduler.process_due_notifications",
	],
	"hourly": [
		"corelytic_erp.corelytic_assessment.scheduler.send_assessment_reminders",
		"corelytic_erp.corelytic_assessment.scheduler.expire_pending_assignments",
	],
	"daily": [
		"corelytic_erp.corelytic_assessment.scheduler.recompute_results",
		# Corelytic AI
		"corelytic_erp.corelytic_ai.tools.discovery.sync_tool_configurations",
		"corelytic_erp.corelytic_ai.utils.cleanup_old_logs",
		# Corelytic Interview: recording / transcript retention
		"corelytic_erp.corelytic_interview.services.retention.run",
	],
}

# WhatsApp providers: name -> class implementing
# corelytic_erp.corelytic_whatsapp.services.whatsapp_provider.WhatsAppProvider.
whatsapp_providers = {
	"eValidation": "corelytic_erp.corelytic_whatsapp.services.providers.evalidation.EValidationProvider",
	"Evolution API": "corelytic_erp.corelytic_whatsapp.services.providers.evolution.EvolutionProvider",
}

default_log_clearing_doctypes = {
	"WhatsApp Notification Log": 180,
}


# ---------------------------------------------------------------------------
# Corelytic Assessment (module corelytic_erp/corelytic_assessment, merged from
# the former akash_recruitment_assessment app). See docs/recruitment.md.
# Install / migrate / uninstall and the Job Applicant event are registered above.
# ---------------------------------------------------------------------------

# Desk form scripts. Files live in public/js/corelytic_assessment/.
doctype_js = {
	"Job Applicant": [
		"public/js/corelytic_assessment/job_applicant.js",
		# Actions > Delete Candidate Data (candidate_data.py): applicant + interviews + logs.
		"public/js/candidate_data.js",
	],
	"Job Opening": "public/js/corelytic_assessment/job_opening.js",
	"Corelytic Assessment Assignment": "public/js/corelytic_assessment/assessment_assignment.js",
	"Corelytic Assessment Attempt": "public/js/corelytic_assessment/assessment_attempt.js",
	"Corelytic Assessment Template": "public/js/corelytic_assessment/assessment_template.js",
}
doctype_list_js = {
	"Job Applicant": "public/js/corelytic_assessment/job_applicant_list.js",
	"Corelytic Assessment Assignment": "public/js/corelytic_assessment/assessment_assignment_list.js",
}

# Candidate portal: www/assessment-portal (loads public/js/corelytic_assessment/proctoring.js).
website_route_rules = [
	{"from_route": "/assessment-portal/<path:app_path>", "to_route": "assessment-portal"},
]
website_context = {
	"favicon": "/assets/frappe/images/favicon.png",
}

# Job Applicant > Interview / Assessment summary also lists open assessments.
override_whitelisted_methods = {
	"hrms.hr.doctype.job_applicant.job_applicant.get_interview_details": "corelytic_erp.corelytic_assessment.integration.get_interview_details",
}

# Renames on 2026-11-08: app grid_erp -> corelytic_erp, then module recruitment_assessment ->
# corelytic_assessment. URLs with the old method paths stay valid: WhatsApp providers call the
# webhook URL they were given, candidates and sent emails hold links, and open browser tabs still
# have old pages. Only public / linked endpoints are listed.
# (old paths, new module path, functions); every old path is tried under every old app name.
_ASSESSMENT_API = [
	"candidate_auth", "get_public_assignment_context", "candidate_context", "accept_consent", "reject_consent",
	"get_assessment", "start_attempt", "start_assessment", "autosave_answers", "upload_answer_file",
	"save_violation", "save_audit_log", "log_violation", "upload_screen_recording", "upload_camera_recording",
	"upload_microphone_recording", "save_snapshot", "heartbeat", "upload_recording", "complete_attempt",
	"submit_assessment", "get_results",
]
_RENAMED_PUBLIC_METHODS = [
	(["assets"], "assets", ["serve"]),
	(["grid_whatsapp.api.webhook"], "corelytic_whatsapp.api.webhook", ["status_callback"]),
	(["grid_interview.api.portal"], "corelytic_interview.api.portal", ["register", "submit_reference_response", "download_document"]),
	(["grid_interview.api.recording"], "corelytic_interview.api.recording", ["consent_status", "set_consent", "ingest_start", "ingest_chunk", "ingest_complete"]),
	(["grid_interview.api.video"], "corelytic_interview.api.video", ["room_info", "join", "heartbeat", "leave", "redeem_link"]),
	(["recruitment_assessment.certificate"], "corelytic_assessment.certificate", ["generate_certificate", "certificate_available"]),
	(["recruitment_assessment.api"], "corelytic_assessment.api", _ASSESSMENT_API),
	(["recruitment_assessment.proxy_detection"], "corelytic_assessment.proxy_detection", ["check_proxy_for_attempt"]),
]
for _olds, _new, _functions in _RENAMED_PUBLIC_METHODS:
	for _app in ("grid_erp", "corelytic_erp"):
		for _old in _olds:
			if (_app, _old) == ("corelytic_erp", _new) or _old == "assets" and _app == "corelytic_erp":
				continue  # that is the current path
			for _fn in _functions:
				override_whitelisted_methods[f"{_app}.{_old}.{_fn}"] = f"corelytic_erp.{_new}.{_fn}"

fixtures = [
	{
		"doctype": "Email Template",
		"filters": [["name", "=", "Assessment Invitation"]],
	},
]


# ---------------------------------------------------------------------------
# Corelytic AI (module corelytic_erp/corelytic_ai, merged from the former grid_ai app).
# See docs/ai.md. Install / migrate, the DocType event and the daily jobs are
# registered above. On the desk: Corelytic ERP tile > AI Assistant (sidebar of module
# Corelytic AI). The page itself checks AI Settings > Allowed Roles.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Corelytic Interview (module corelytic_erp/corelytic_interview, merged from the former
# corelytic_interview app). See docs/interview.md. Install / migrate, the 5-minute
# cycle and the daily retention job are registered above. It adds no hooks on
# HRMS DocTypes: Desk changes to HRMS Interviews are picked up by the cycle.
# ---------------------------------------------------------------------------

# Candidates (Website Users with role Corelytic Interview Candidate) land on the candidate portal.
get_website_user_home_page = "corelytic_erp.corelytic_interview.permissions.website_user_home_page"
portal_menu_items = [
	{"title": "Candidate Portal", "route": "/candidate-portal", "role": "Corelytic Interview Candidate"},
]
# Links in emails sent before the merge pointed to /interview-portal.
website_redirects = [
	{"source": r"/interview-portal(/.*)?", "target": r"/candidate-portal\1"},
]

# Interviewers see only the sessions / transcripts / analyses of their own interviews.
permission_query_conditions = {
	"Corelytic Interview Video Session": "corelytic_erp.corelytic_interview.permissions.video_session_query",
	"Corelytic Interview Transcript": "corelytic_erp.corelytic_interview.permissions.interview_linked_query",
	"Corelytic Interview Analysis": "corelytic_erp.corelytic_interview.permissions.interview_linked_query",
}
