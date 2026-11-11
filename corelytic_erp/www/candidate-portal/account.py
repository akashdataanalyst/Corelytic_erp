from frappe import _

from corelytic_erp.corelytic_interview.services import portal
from corelytic_erp.corelytic_interview.www_helpers import candidate_page, fmt

no_cache = 1
no_sitemap = 1


def get_context(context):
	context.title = _("Account")
	profile = candidate_page(context, "account", "/candidate-portal/account")
	if not profile:
		return context
	history = portal.notification_history(profile)
	for h in history:
		h["when"] = fmt(h["creation"], "d MMM yyyy, HH:mm")
	context.history = history
	context.email = profile.email
	context.loaded = True
	return context
