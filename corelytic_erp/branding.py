"""Corelytic Branding Settings: serving the values and locking the form.

1. Branding values reach the desk through boot and website/login pages through
   an inline script in <head>, so calco_branding.js renders the configured logo,
   text and colours without a flash of the defaults.
2. Only the Administrator user may edit, and only after entering the branding
   password, which unlocks editing for UNLOCK_SECONDS in that login session."""

import time

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit
from frappe.utils.password import passlibctx

DOCTYPE = "Corelytic Branding Settings"
EDITOR = "Administrator"
# Only a hash of the edit password is kept, never the password itself. Every site
# uses DEFAULT_PASSWORD_HASH unless site_config.json sets PASSWORD_HASH_KEY.
PASSWORD_HASH_KEY = "corelytic_branding_password_hash"
DEFAULT_PASSWORD_HASH = "$pbkdf2-sha256$29000$yvnfO8fYew9hTKk1BkBobQ$tLTLWkPD88q8k773qQDSR0jnDz5M3Xf6qcck8wsJlfk"
UNLOCK_SECONDS = 15 * 60

BRAND_FIELDS = {
	"company_name": "companyName",
	"app_name": "appName",
	"login_title": "loginTitle",
	"erp_title": "erpTitle",
	"tagline": "tagline",
	"capabilities": "capabilities",
	"description": "description",
	"footer_line": "footerLine",
	"logo": "logoUrl",
	"favicon": "faviconUrl",
	"banner_image": "bannerUrl",
	"primary_color": "primaryColor",
	"primary_deep_color": "primaryDeepColor",
	"header_color": "headerColor",
	"text_color": "textColor",
	"page_color": "pageColor",
}

TEXT_FIELDS = {
	"login_heading": "loginHeading",
	"login_subtitle_prefix": "loginSubtitlePrefix",
	"authorized_access": "authorizedAccess",
	"secure_connection": "secureConnection",
	"workspace_heading": "workspaceHeading",
}


# ---------------------------------------------------------------------------
# 1. Branding values
# ---------------------------------------------------------------------------


def get_branding():
	"""Only filled-in values are returned; blank fields keep the built-in defaults."""
	try:
		settings = frappe.get_cached_doc(DOCTYPE)
	except Exception:
		# DocType not migrated yet: fall back to the defaults in calco_workspace_config.js.
		return {}

	def pick(fields):
		return {key: settings.get(field).strip() for field, key in fields.items() if (settings.get(field) or "").strip()}

	branding = {"brand": pick(BRAND_FIELDS), "text": pick(TEXT_FIELDS)}

	values = [v.strip() for v in (settings.banner_values or "").split(",") if v.strip()]
	if values:
		branding["text"]["bannerValues"] = values

	order = [line.strip() for line in (settings.workspace_order or "").splitlines() if line.strip()]
	if order:
		branding["workspaceOrder"] = order

	if (settings.app_version or "").strip():
		branding["appVersion"] = settings.app_version.strip()

	quick_actions = parse_quick_actions(settings.get("quick_actions"))
	if quick_actions is not None:
		branding["quickActions"] = quick_actions

	return branding


def parse_quick_actions(text):
	"""'DocType | Label | Hint' per line -> [[doctype, label, hint], ...].
	None when empty (the defaults in calco_workspace_config.js apply), [] for "none"."""
	text = (text or "").strip()
	if not text:
		return None
	if text.lower() == "none":
		return []
	actions = []
	for line in text.splitlines():
		parts = [part.strip() for part in line.split("|")]
		if not parts[0]:
			continue
		doctype = parts[0]
		label = parts[1] if len(parts) > 1 and parts[1] else _("New {0}").format(_(doctype))
		hint = parts[2] if len(parts) > 2 else ""
		actions.append([doctype, label, hint])
	return actions


def boot_session(bootinfo):
	bootinfo.calco_branding = get_branding()


def update_website_context(context):
	payload = frappe.as_json(get_branding(), indent=None).replace("</", "<\\/")
	script = f"<script>window.calcoBrandingSettings = {payload};</script>"
	# head_html is rendered on every website page, login included (login.html
	# overrides the head_include block). Keep any Website Settings head HTML.
	return {"head_html": (context.get("head_html") or "") + script}


# ---------------------------------------------------------------------------
# 2. Edit lock
# ---------------------------------------------------------------------------


def has_permission(doc, ptype=None, user=None, debug=False):
	return (user or frappe.session.user) == EDITOR


def ensure_editor():
	if frappe.session.user != EDITOR:
		frappe.throw(_("Only Administrator can change branding settings."), frappe.PermissionError)


def _unlock_key():
	return f"corelytic_branding_unlocked:{frappe.session.sid}"


def unlocked_seconds_left():
	"""Seconds until the edit lock closes again, 0 when locked."""
	if frappe.session.user != EDITOR:
		return 0
	until = frappe.cache.get_value(_unlock_key())
	if not until:
		return 0
	return max(0, int(float(until) - time.time()))


def is_unlocked():
	return unlocked_seconds_left() > 0


def extend_unlock():
	"""(Re)start the UNLOCK_SECONDS window: on unlock and on every save, so the
	editor is not asked again while they keep working."""
	frappe.cache.set_value(_unlock_key(), time.time() + UNLOCK_SECONDS, expires_in_sec=UNLOCK_SECONDS)


@frappe.whitelist(methods=["POST"])
@rate_limit(limit=5, seconds=5 * 60)
def unlock(password):
	"""Unlock editing for this login session for UNLOCK_SECONDS."""
	ensure_editor()
	password_hash = frappe.conf.get(PASSWORD_HASH_KEY) or DEFAULT_PASSWORD_HASH
	if not password or not passlibctx.verify(password, password_hash):
		# Not AuthenticationError: Frappe clears the login cookies on that one,
		# which logs the user out ("Your session has expired").
		frappe.throw(_("Incorrect password."), frappe.ValidationError)
	extend_unlock()
	return unlocked_seconds_left()


@frappe.whitelist()
def unlock_status():
	"""Seconds the form stays editable; 0 when the password is needed."""
	return unlocked_seconds_left()
