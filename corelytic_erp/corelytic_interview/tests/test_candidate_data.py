"""Job Applicant > Delete Candidate Data (corelytic_erp/candidate_data.py)."""

from unittest.mock import patch

import frappe
from frappe.utils import add_days, nowdate

from corelytic_erp import candidate_data
from corelytic_erp.corelytic_interview.services import scheduling
from corelytic_erp.corelytic_interview.tests.utils import (
	INTERVIEW_TYPE,
	RollbackTestCase,
	make_applicant,
	make_interview_type,
	make_user,
	needs_hrms,
)

GI = "Corelytic Interview "


def _assign(applicant: str):
	from corelytic_erp.corelytic_assessment.service import RecruitmentAssessmentService

	template = frappe.get_all("Corelytic Assessment Template", pluck="name", limit=1)
	if not template:
		return None
	return RecruitmentAssessmentService().create_assignment(applicant, template[0])


@needs_hrms
class TestDeleteCandidateData(RollbackTestCase):
	def setUp(self):
		super().setUp()
		make_interview_type()
		self.interviewer = make_user("gi.del.int@example.com", ["Interviewer"])
		self.applicant = make_applicant("delete.me@example.com", "Delete Me")
		scheduling.schedule_interview(
			self.applicant, INTERVIEW_TYPE, add_days(nowdate(), 3), "10:00:00", "11:00:00", [self.interviewer]
		)
		self.assignment = _assign(self.applicant)
		self.session = frappe.get_all(GI + "Video Session", {"job_applicant": self.applicant}, pluck="name")[0]
		self.interview = frappe.db.get_value(GI + "Video Session", self.session, "interview")

	def test_summary_lists_the_chain(self):
		counts = candidate_data.get_delete_summary(self.applicant)["counts"]
		self.assertEqual(counts["Interview"], 1)
		self.assertEqual(counts[GI + "Video Session"], 1)
		self.assertGreater(counts[GI + "Notification Log"], 0)
		self.assertGreater(counts[GI + "Audit Log"], 0)
		if self.assignment:
			self.assertEqual(counts["Corelytic Assessment Assignment"], 1)

	def test_deletes_applicant_and_everything_linked(self):
		# another candidate's records must stay
		other = make_applicant("keep.me@example.com", "Keep Me")
		scheduling.schedule_interview(other, INTERVIEW_TYPE, add_days(nowdate(), 4), "10:00:00", "11:00:00", [self.interviewer])
		other_session = frappe.get_all(GI + "Video Session", {"job_applicant": other}, pluck="name")[0]

		candidate_data.delete_candidate_data(self.applicant, confirm=self.applicant)

		self.assertFalse(frappe.db.exists("Job Applicant", self.applicant))
		self.assertFalse(frappe.db.exists("Interview", self.interview))
		self.assertFalse(frappe.db.exists(GI + "Video Session", self.session))
		deleted = {GI + "Video Session": self.session, "Interview": self.interview, "Job Applicant": self.applicant}
		for log in (GI + "Notification Log", GI + "Audit Log"):
			for doctype, name in deleted.items():
				self.assertFalse(frappe.get_all(log, {"reference_doctype": doctype, "reference_name": name}), f"{log} → {doctype}")
		# the candidate's portal account (User, same email here) and its audit rows are kept
		self.assertTrue(frappe.db.exists("User", "delete.me@example.com"))
		if self.assignment:
			self.assertFalse(frappe.db.exists("Corelytic Assessment Assignment", self.assignment.name))
		# one summary audit row for the delete itself
		row = frappe.get_all(GI + "Audit Log", {"action": "candidate.data_deleted"}, ["metadata"], order_by="creation desc", limit=1)
		self.assertIn(self.applicant, row[0].metadata)
		# untouched
		self.assertTrue(frappe.db.exists("Job Applicant", other))
		self.assertTrue(frappe.db.exists(GI + "Video Session", other_session))
		self.assertTrue(frappe.get_all(GI + "Notification Log", {"reference_name": other_session}))

	def test_submitted_interview_is_deleted(self):
		frappe.db.set_value("Interview", self.interview, {"docstatus": 1, "status": "Cleared"})
		candidate_data.delete_candidate_data(self.applicant, confirm=self.applicant)
		self.assertFalse(frappe.db.exists("Interview", self.interview))

	def test_wrong_confirmation_deletes_nothing(self):
		with self.assertRaises(frappe.ValidationError):
			candidate_data.delete_candidate_data(self.applicant, confirm="yes")
		self.assertTrue(frappe.db.exists("Job Applicant", self.applicant))

	def test_only_administrators(self):
		hr = make_user("gi.del.hr@example.com", ["HR Manager", "HR User"])
		frappe.set_user(hr)
		try:
			with self.assertRaises(frappe.PermissionError):
				candidate_data.delete_candidate_data(self.applicant, confirm=self.applicant)
			with self.assertRaises(frappe.PermissionError):
				candidate_data.get_delete_summary(self.applicant)
		finally:
			frappe.set_user("Administrator")
		self.assertTrue(frappe.db.exists("Job Applicant", self.applicant))

	def test_hiring_records_block_the_delete(self):
		frappe.get_doc(
			{"doctype": GI + "Reference", "applicant_doctype": "Job Applicant", "job_applicant": self.applicant,
			 "referee_name": "Ref Erence", "email": "ref@example.com"}
		).insert(ignore_permissions=True, ignore_mandatory=True)
		with patch.object(candidate_data, "BLOCKING_DOCTYPES", (GI + "Reference",)):
			self.assertTrue(candidate_data.get_delete_summary(self.applicant)["blockers"])
			with self.assertRaises(frappe.ValidationError):
				candidate_data.delete_candidate_data(self.applicant, confirm=self.applicant)
		self.assertTrue(frappe.db.exists("Job Applicant", self.applicant))
