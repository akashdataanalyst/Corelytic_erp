"""OpenRouter provider (OpenAI-compatible API at https://openrouter.ai/api/v1)."""

import frappe

from corelytic_erp.corelytic_ai.ai.providers.openai import OpenAICompatibleProvider


class OpenRouterProvider(OpenAICompatibleProvider):
	name = "OpenRouter"

	def headers(self) -> dict:
		headers = super().headers()
		# Optional attribution headers recommended by OpenRouter.
		headers["HTTP-Referer"] = frappe.utils.get_url()
		headers["X-Title"] = "Corelytic AI"
		return headers

	def payload(self, messages, tools, stream):
		payload = super().payload(messages, tools, stream)
		if stream:
			payload["usage"] = {"include": True}
		return payload
