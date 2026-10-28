"""Behavior tests use invented accounts and employers; no mailbox access."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import application_index as ai


EMAIL = "candidate@example.test"
START = "2026-08-29T03:00:00Z"
END = "2026-10-28T16:00:00Z"


def message(mid, req=None, title="Developer 2027", kind="application_submitted",
            timestamp="2026-10-27T12:00:00Z", **extra):
    event = {"company": "Example Co", "title": title, "type": kind,
             "confidence": "high", "excerpt": "Synthetic application evidence."}
    if req is not None:
        event["requisition_id"] = req
    event.update(extra)
    return {"message_id": mid, "received_at": timestamp,
            "url": "https://mail.google.com/mail/u/0/#all/" + mid,
            "disposition": "application", "events": [event]}


def batch(messages, start=START, end=END, complete=True, **scan):
    return {"account_email": EMAIL,
            "scan": {"start": start, "end": end, "complete": complete, **scan},
            "messages": messages}


class IndexBehavior(unittest.TestCase):
    def setUp(self):
        self.empty = ai.new_index(EMAIL)

    def test_duplicate_message_replays_do_not_duplicate_events_or_revision(self):
        first = ai.ingest(self.empty, batch([message("m1", "R-2027")]))
        again = ai.ingest(first, batch([message("m1", "R-2027")]))
        self.assertEqual(first, again)
        self.assertEqual(len(again["processed_messages"]), 1)
        result = ai.lookup(again, "Example Co", requisition_id="R-2027")
        self.assertEqual(result["match"], "exact")
        self.assertEqual(len(result["applications"][0]["events"]), 1)

    def test_different_requisitions_and_cohorts_do_not_merge(self):
        index = ai.ingest(self.empty, batch([
            message("old", "R-2026", title="Developer 2026"),
            message("new", "R-2027"),
            message("title1", title="Graduate 2026"),
            message("title2", title="Graduate 2027"),
        ]))
        self.assertEqual(len(index["applications"]), 4)
        result = ai.lookup(index, "Example Co", requisition_id="R-2028")
        self.assertNotEqual(result["match"], "exact")
        self.assertFalse(result["applied_confirmed"])
        self.assertEqual(ai.lookup(index, "Example Co", title="Graduate 2027")["match"], "exact")

    def test_generic_and_truncated_receipts_stay_unresolved(self):
        index = ai.ingest(self.empty, batch([
            message("generic", title=None),
            message("prefix", "98765", requisition_id_truncated=True),
        ]))
        result = ai.lookup(index, "Example Co", requisition_id="987654")
        self.assertEqual(result["match"], "possible")
        self.assertFalse(result["applied_confirmed"])
        self.assertTrue(all(a["identity_confidence"] == "unresolved"
                            for a in result["applications"]))

    def test_partial_scan_keeps_cursor_and_resumes_fixed_window(self):
        index = ai.ingest(self.empty, batch([message("old", "R-1")]))
        partial = ai.ingest(index, batch([
            message("new", "R-2", timestamp="2026-10-28T17:00:00Z")
        ], start="2026-10-26T16:00:00Z", end="2026-10-28T18:00:00Z",
            complete=False, next_page_token="next-page"))
        self.assertEqual(partial["coverage"]["end"], END)
        self.assertEqual(ai.lookup(partial, "Example Co", requisition_id="R-2")["match"], "exact")
        planned = ai.plan(partial, "2026-10-29T20:00:00Z")
        self.assertEqual(planned["scan"]["end"], "2026-10-28T18:00:00Z")
        self.assertEqual(planned["scan"]["next_page_token"], "next-page")
        finished = ai.ingest(partial, batch([], start="2026-10-26T16:00:00Z",
                                         end="2026-10-28T18:00:00Z"))
        self.assertEqual(finished["coverage"]["end"], "2026-10-28T18:00:00Z")
        self.assertIsNone(finished["pending_scan"])

    def test_rejection_is_not_overwritten_by_later_task_reminder(self):
        index = ai.ingest(self.empty, batch([
            message("receipt", "R-1", timestamp="2026-10-24T12:00:00Z"),
            message("decision", "R-1", kind="rejected", timestamp="2026-10-25T12:00:00Z"),
            message("task", "R-1", kind="action_required", timestamp="2026-10-26T12:00:00Z",
                    action={"kind": "questionnaire", "description": "Complete questions",
                            "state": "requested"}),
            message("closed", "R-2", kind="role_closed"),
        ]))
        application = ai.lookup(index, "Example Co", requisition_id="R-1")["applications"][0]
        self.assertEqual(application["status"], "rejected")
        self.assertTrue(application["applied_confirmed"])
        self.assertEqual(application["actions"][0]["state"], "requested")
        self.assertEqual(application["actions"][0]["completion_evidence"], False)
        self.assertEqual(ai.lookup(index, "Example Co", requisition_id="R-2")["applications"][0]["status"], "role_closed")

    def test_account_mismatch_and_conflicting_message_are_rejected_without_mutation(self):
        wrong = batch([message("m1", "R-1")])
        wrong["account_email"] = "someone-else@example.test"
        with self.assertRaises(ValueError):
            ai.ingest(self.empty, wrong)
        original = ai.ingest(self.empty, batch([message("m1", "R-1")]))
        snapshot = copy.deepcopy(original)
        with self.assertRaises(ValueError):
            ai.ingest(original, batch([message("m1", "R-2")]))
        self.assertEqual(original, snapshot)

    def test_plan_uses_local_calendar_days_then_overlap_and_known_ids(self):
        initial = ai.plan(self.empty, "2026-10-28T21:00:00Z")
        self.assertEqual(initial["scan"]["start"], START)
        self.assertIn("after:", initial["gmail_query"])
        self.assertIn("before:", initial["gmail_query"])
        index = ai.ingest(self.empty, batch([message("m1", "R-1")]))
        delta = ai.plan(index, "2026-10-28T21:00:00Z")
        self.assertEqual(delta["scan"]["start"], "2026-10-26T16:00:00Z")
        self.assertEqual(delta["scan"]["end"], "2026-10-28T21:00:00Z")
        self.assertIn("m1", delta["known_message_ids"])

    def test_backfill_extends_coverage_without_dropping_newer_messages(self):
        index = ai.ingest(self.empty, batch([message("recent", "R-2")]))
        planned = ai.plan(index, "2026-10-28T21:00:00Z", days=90)
        self.assertEqual(planned["scan"]["start"], "2026-07-30T03:00:00Z")
        self.assertEqual(planned["scan"]["end"], START)
        backfilled = ai.ingest(index, batch([
            message("older", "R-1", timestamp="2026-08-01T12:00:00Z")
        ], start=planned["scan"]["start"], end=START))
        self.assertEqual(backfilled["coverage"]["start"], "2026-07-30T03:00:00Z")
        self.assertEqual(backfilled["coverage"]["end"], END)
        self.assertEqual(set(backfilled["processed_messages"]), {"recent", "older"})

    def test_disjoint_complete_windows_do_not_claim_gap_coverage(self):
        index = ai.ingest(self.empty, batch([message("old", "R-1")]))
        index = ai.ingest(index, batch([], start="2026-11-01T00:00:00Z",
                                      end="2026-11-02T00:00:00Z"))
        self.assertEqual(index["coverage"]["end"], END)
        self.assertEqual(len(index["coverage"]["segments"]), 2)

    def test_compare_and_swap_refuses_stale_writer(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "index.json"
            ai.save_index(path, self.empty, expected_revision=None)
            first = ai.ingest(self.empty, batch([message("m1", "R-1")]))
            ai.save_index(path, first, expected_revision=0)
            stale = ai.ingest(self.empty, batch([message("m2", "R-2")]))
            with self.assertRaises(ValueError):
                ai.save_index(path, stale, expected_revision=0)
            self.assertEqual(json.loads(path.read_text())["revision"], 1)
            self.assertEqual(set(json.loads(path.read_text())["processed_messages"]), {"m1"})

    def test_low_confidence_classification_is_not_a_confirmed_application(self):
        index = ai.ingest(self.empty, batch([message("uncertain", "R-1", confidence="low")]))
        result = ai.lookup(index, "Example Co", requisition_id="R-1")
        self.assertFalse(result["applied_confirmed"])

    def test_screening_passed_is_not_an_interview_invitation(self):
        index = ai.ingest(self.empty, batch([
            message("review", "R-1", kind="application_under_review", timestamp="2026-10-25T12:00:00Z"),
            message("screen", "R-1", kind="screening_passed", timestamp="2026-10-26T12:00:00Z"),
        ]))
        result = ai.lookup(index, "Example Co", requisition_id="R-1")
        self.assertTrue(result["applied_confirmed"])
        self.assertEqual(result["applications"][0]["status"], "screening_passed")

    def test_latest_response_exposes_screening_reply_without_regressing_assessment_stage(self):
        index = ai.ingest(self.empty, batch([
            message("assessment", "R-1", kind="assessment_requested", confidence="medium",
                    timestamp="2026-10-25T12:00:00Z"),
            message("screening", "R-1", kind="screening_passed",
                    timestamp="2026-10-26T12:00:00Z", excerpt="You passed our initial screening."),
        ]))
        application = ai.lookup(index, "Example Co", requisition_id="R-1")["applications"][0]
        self.assertEqual(application["status"], "assessment_requested")
        self.assertEqual(application["status_message_id"], "assessment")
        self.assertEqual(application["status_confidence"], "medium")
        latest = application["latest_response"]
        self.assertEqual(latest["type"], "screening_passed")
        self.assertEqual(latest["message_id"], "screening")
        self.assertEqual(latest["confidence"], "high")
        self.assertEqual(latest["occurred_at"], "2026-10-26T12:00:00Z")
        self.assertEqual(latest["received_at"], "2026-10-26T12:00:00Z")
        self.assertEqual(latest["excerpt"], "You passed our initial screening.")
        self.assertTrue(latest["url"].endswith("screening"))

    def test_latest_unknown_score_response_does_not_erase_submission_status(self):
        index = ai.ingest(self.empty, batch([
            message("receipt", "R-1", timestamp="2026-10-25T12:00:00Z"),
            message("score", "R-1", kind="unknown", confidence="medium",
                    timestamp="2026-10-26T12:00:00Z", excerpt="Your score is available."),
        ]))
        application = ai.lookup(index, "Example Co", requisition_id="R-1")["applications"][0]
        self.assertEqual(application["status"], "application_submitted")
        self.assertEqual(application["status_message_id"], "receipt")
        self.assertEqual(application["status_confidence"], "high")
        self.assertEqual(application["latest_response"]["type"], "unknown")
        self.assertEqual(application["latest_response"]["message_id"], "score")
        self.assertEqual(application["latest_response"]["confidence"], "medium")

    def test_same_title_multiple_roles_requires_identity_resolution(self):
        index = ai.ingest(self.empty, batch([
            message("toronto", "R-1", location="Toronto"),
            message("halifax", "R-2", location="Halifax", kind="recruiter_contact"),
        ]))
        result = ai.lookup(index, "Example Co", title="Developer 2027")
        self.assertEqual(result["match"], "possible")
        self.assertFalse(result["applied_confirmed"])
        self.assertEqual(len(result["applications"]), 2)
        self.assertTrue(ai.lookup(index, "Example Co", requisition_id="R-1")["applied_confirmed"])

    def test_vacancy_closure_does_not_replace_candidate_rejection(self):
        index = ai.ingest(self.empty, batch([
            message("decision", "R-1", kind="rejected", timestamp="2026-10-25T12:00:00Z"),
            message("closed", "R-1", kind="role_closed", timestamp="2026-10-26T12:00:00Z"),
        ]))
        application = ai.lookup(index, "Example Co", requisition_id="R-1")["applications"][0]
        self.assertEqual(application["status"], "rejected")
        self.assertTrue(application["role_closed"])

    def test_exact_task_exposes_truncated_receipt_and_explicit_correction_retains_audit(self):
        receipt = message("receipt", "98765", requisition_id_truncated=True)
        task = message("task", "987654", kind="action_required",
                       action={"kind": "questionnaire", "description": "Application questions", "state": "requested"})
        index = ai.ingest(self.empty, batch([receipt]))
        index = ai.ingest(index, batch([task]))
        before = ai.lookup(index, "Example Co", requisition_id="987654")
        self.assertEqual(before["match"], "exact")
        self.assertFalse(before["applied_confirmed"])
        self.assertEqual(before["possible_candidates"][0]["events"][0]["message_id"], "receipt")
        replacement = message("receipt", "987654", related_message_ids=["task"])
        corrected = ai.correct(index, replacement, "Full ID corroborated by matching task email", ["task"])
        after = ai.lookup(corrected, "Example Co", requisition_id="987654")
        self.assertTrue(after["applied_confirmed"])
        self.assertEqual(len(after["applications"][0]["events"]), 2)
        self.assertEqual(after["possible_candidates"], [])
        self.assertEqual(corrected["coverage"], index["coverage"])
        audit = corrected["correction_history"][0]
        self.assertEqual(audit["previous_classification"]["events"][0]["requisition_id"], "98765")
        self.assertEqual(audit["evidence_message_ids"], ["task"])
        self.assertEqual(audit["revision"], index["revision"] + 1)
        self.assertEqual(index["processed_messages"]["receipt"]["events"][0]["requisition_id"], "98765")

    def test_correction_requires_existing_related_evidence_and_immutable_source_identity(self):
        index = ai.ingest(self.empty, batch([
            message("receipt", "98765", requisition_id_truncated=True),
            message("other", "123456", company="Unrelated Employer"),
            message("valid", "987654", kind="action_required"),
        ]))
        replacement = message("receipt", "987654")
        for evidence in ([], ["missing"], ["receipt"], ["other"]):
            with self.subTest(evidence=evidence), self.assertRaises(ValueError):
                ai.correct(index, replacement, "Review of corroborating evidence", evidence)
        with self.assertRaises(ValueError):
            ai.correct(index, replacement, "", ["valid"])
        with self.assertRaises(ValueError):
            ai.correct(index, message("receipt", "987654", timestamp="2026-10-26T12:00:00Z"),
                       "Cannot rewrite email timestamp", ["valid"])

    def test_external_posting_ids_are_namespaced_and_distinct_from_employer_requisitions(self):
        index = ai.ingest(self.empty, batch([
            message("linkedin1", external_job_source="linkedin", external_job_id="123"),
            message("linkedin2", external_job_source="linkedin", external_job_id="456"),
            message("other_board", external_job_source="otherboard", external_job_id="123"),
            message("employer", "123"),
        ]))
        self.assertEqual(len(index["applications"]), 4)
        result = ai.lookup(index, "Example Co", external_job_source="linkedin", external_job_id="123")
        self.assertTrue(result["applied_confirmed"])
        self.assertEqual(len(result["applications"]), 1)
        self.assertEqual(result["applications"][0]["identity_confidence"], "external_job")
        self.assertIsNone(result["applications"][0]["requisition_id"])
        self.assertEqual(result["applications"][0]["events"][0]["message_id"], "linkedin1")
        self.assertEqual(ai.lookup(index, "Example Co", requisition_id="123")["applications"][0]["events"][0]["message_id"], "employer")
        with self.assertRaises(ValueError):
            ai.lookup(index, "Example Co", external_job_id="123")

    def test_req_based_events_preserve_explicit_external_aliases_without_automatic_merging(self):
        index = ai.ingest(self.empty, batch([
            message("receipt", "R-7", external_job_source="linkedin", external_job_id="123"),
            message("decision", "R-7", kind="rejected", external_job_source="linkedin", external_job_id="456"),
            message("separate", external_job_source="linkedin", external_job_id="123"),
        ]))
        self.assertEqual(len(index["applications"]), 2)
        result = ai.lookup(index, "Example Co", external_job_source="linkedin", external_job_id="456")
        self.assertEqual(result["applications"][0]["requisition_id"], "R-7")
        self.assertEqual(result["applications"][0]["status"], "rejected")
        ambiguous = ai.lookup(index, "Example Co", external_job_source="linkedin", external_job_id="123")
        self.assertEqual(ambiguous["match"], "possible")
        self.assertFalse(ambiguous["applied_confirmed"])
        self.assertEqual(len(ambiguous["applications"]), 2)
        self.assertIn("example co|linkedin|123", index["lookup"]["external_jobs"])

    def test_gmail_query_overfetches_boundary_but_ingest_enforces_logical_interval(self):
        planned = ai.plan(self.empty, "2026-10-28T21:00:00Z")
        self.assertIn("after:" + str(int(ai.dt(START).timestamp()) - 1), planned["gmail_query"])
        with self.assertRaises(ValueError):
            ai.ingest(self.empty, batch([message("boundary", "R-1", timestamp=END)]))

    def test_cli_init_ingest_and_lookup_round_trip(self):
        script = str(Path(ai.__file__).resolve())
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "index.json")
            batch_path = Path(directory) / "batch.json"
            batch_path.write_text(json.dumps(batch([message("cli", "R-1")])))
            def run(*arguments):
                result = subprocess.run([sys.executable, script, *arguments, "--index", path],
                                        capture_output=True, text=True, check=True)
                return json.loads(result.stdout)
            self.assertEqual(run("init", "--account", EMAIL)["revision"], 0)
            self.assertEqual(run("ingest", "--batch", str(batch_path),
                                 "--expected-revision", "0")["applications"], 1)
            self.assertTrue(run("lookup", "--company", "Example Co", "--requisition", "R-1")["applied_confirmed"])

    def test_cli_correction_persists_audit_and_rejects_stale_revision(self):
        script = str(Path(ai.__file__).resolve())
        index = ai.ingest(self.empty, batch([
            message("receipt", "98765", requisition_id_truncated=True),
            message("task", "987654", kind="action_required", external_job_source="linkedin", external_job_id="123"),
        ]))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "index.json"
            replacement_path = Path(directory) / "replacement.json"
            ai.save_index(path, index, expected_revision=None)
            replacement_path.write_text(json.dumps(message("receipt", "987654")))
            command = [sys.executable, script, "correct", "--index", str(path),
                       "--message", str(replacement_path), "--reason", "Matching full ID in task",
                       "--evidence-id", "task", "--expected-revision", str(index["revision"])]
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            self.assertEqual(json.loads(result.stdout)["revision"], index["revision"] + 1)
            self.assertEqual(len(ai.load_index(path)["correction_history"]), 1)
            stale = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(stale.returncode, 2)
            self.assertIn("Revision conflict", json.loads(stale.stderr)["error"])
            lookup = subprocess.run([sys.executable, script, "lookup", "--index", str(path),
                                     "--company", "Example Co", "--external-job-source", "linkedin",
                                     "--external-job-id", "123"], capture_output=True, text=True, check=True)
            self.assertTrue(json.loads(lookup.stdout)["applied_confirmed"])


if __name__ == "__main__":
    unittest.main()
