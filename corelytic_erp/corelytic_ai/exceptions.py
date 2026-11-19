"""Exceptions carrying a short, user-safe message.

Anything shown to the user comes from `user_message`; technical details only go to the Error Log.
"""


class CorelyticAIError(Exception):
	code = "error"
	log_status = "Error"
	default_message = "Sorry, data retrieve karte time problem aayi."

	def __init__(self, user_message: str | None = None, *, detail: str | None = None):
		self.user_message = user_message or self.default_message
		self.detail = detail
		super().__init__(detail or self.user_message)


class PermissionDeniedError(CorelyticAIError):
	code = "permission_denied"
	log_status = "Denied"
	default_message = "Aapko is data ko access karne ki permission nahi hai."


class NotConfiguredError(CorelyticAIError):
	code = "not_configured"
	log_status = "Not Configured"
	default_message = "Ye data AI ke liye configured nahi hai."


class InvalidRequestError(CorelyticAIError):
	code = "invalid_request"
	log_status = "Invalid"
	default_message = "Request samajh nahi aayi. Kripya sawal thoda clear karke poochiye."


class RateLimitError(CorelyticAIError):
	code = "rate_limited"
	log_status = "Rate Limited"
	default_message = "Bahut zyada requests aa gayi hain. Thodi der baad try kariye."


class TokenLimitError(CorelyticAIError):
	code = "token_limit"
	log_status = "Rate Limited"
	default_message = "Aaj ki AI usage limit poori ho gayi hai. Kal dobara try kariye."


class AssistantDisabledError(CorelyticAIError):
	code = "disabled"
	log_status = "Denied"
	default_message = "AI Assistant abhi enabled nahi hai. Administrator se contact kariye."
