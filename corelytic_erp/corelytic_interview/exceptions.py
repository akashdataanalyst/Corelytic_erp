"""Error types the app raises on purpose; each maps to a clear message for the user."""

import frappe


class CorelyticInterviewError(frappe.ValidationError):
	"""Base class for expected, user-facing corelytic_interview errors."""


class HRMSNotAvailable(CorelyticInterviewError):
	"""HRMS (Interview, Job Applicant, ...) is not installed on this site."""


class AccessDenied(frappe.PermissionError):
	"""The caller may not access the requested interview resource."""


class InvalidAccessToken(AccessDenied):
	"""Unknown, expired, revoked or mis-bound access token. The message never says which."""


class OutsideJoinWindow(CorelyticInterviewError):
	"""The interview cannot be joined at this time."""
