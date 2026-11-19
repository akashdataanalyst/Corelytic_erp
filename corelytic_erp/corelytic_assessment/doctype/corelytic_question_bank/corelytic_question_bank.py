from __future__ import annotations

import frappe
from frappe import _

from corelytic_erp.corelytic_assessment.base import BaseAssessmentDocument


class CorelyticQuestionBank(BaseAssessmentDocument):
	def validate(self):
		if self.question_type == "Single Choice MCQ" and not self.options:
			frappe.throw(_("MCQ questions require at least one option."))

