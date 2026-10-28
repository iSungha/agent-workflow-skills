#!/usr/bin/env python3
"""Portable Gmail application index. JSON in/out; no network or credentials.

This engine accepts already classified email evidence. It does not infer facts
from raw mail and must not be used to declare unscanned mail fully covered.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, time, timedelta, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile
import unicodedata
from zoneinfo import ZoneInfo


UTC = timezone.utc
EVENT_TYPES = {
    "application_submitted", "application_incomplete", "application_viewed",
    "application_under_review", "screening_passed",
    "assessment_requested", "assessment_completed", "interview_invited",
    "interview_scheduled", "interview_completed", "offer_received", "offer_accepted",
    "rejected", "withdrawn", "role_closed", "hired", "recruiter_contact",
    "action_required", "action_completed", "unknown",
}
STAGES = {name: rank for rank, name in enumerate([
    "unknown", "recruiter_contact", "application_incomplete", "application_submitted",
    "application_viewed", "application_under_review", "screening_passed",
    "assessment_requested", "assessment_completed",
    "interview_invited", "interview_scheduled", "interview_completed",
    "offer_received", "offer_accepted", "hired",
])}
TERMINAL = {"rejected", "withdrawn", "role_closed", "hired"}
APPLIED_TYPES = EVENT_TYPES - {
    "unknown", "recruiter_contact", "application_incomplete", "role_closed",
    "action_required", "action_completed",
}


def dt(value):
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Timestamps must include a timezone")
    return parsed.astimezone(UTC)


def iso(value):
    return value.astimezone(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def norm(value):
    value = unicodedata.normalize("NFKC", str(value or "")).casefold()
    return " ".join(re.findall(r"\w+", value, re.UNICODE))


def reqnorm(value):
    return "".join(unicodedata.normalize("NFKC", str(value or "")).upper().split())


def account(value):
    value = str(value or "").strip().casefold()
    if not value or "@" not in value:
        raise ValueError("A stable account email is required")
    return value


def positive_days(days):
    if isinstance(days, bool) or not isinstance(days, int) or days < 1:
        raise ValueError("days must be a positive integer")
    return days


def new_index(email, days=60, timezone="America/Halifax"):
    ZoneInfo(timezone)
    return {
        "schema_version": 1,
        "revision": 0,
        "account_email": account(email),
        "timezone": timezone,
        "config": {"initial_days": positive_days(days), "overlap_hours": 48},
        "coverage": {"start": None, "end": None, "segments": [],
                     "scope": "all_mail_metadata_excluding_drafts"},
        "pending_scan": None,
        "processed_messages": {},
        "correction_history": [],
        "applications": {},
        "lookup": {"companies": {}, "requisitions": {}, "external_jobs": {}, "titles": {}},
    }


def check_index(index):
    if index.get("schema_version") != 1:
        raise ValueError("Unsupported index schema; do not overwrite it")
    account(index.get("account_email"))
    if not isinstance(index.get("processed_messages"), dict):
        raise ValueError("Invalid processed_messages map")


def plan(index, now=None, days=None):
    """Return one immutable scan window, resuming incomplete work first."""
    check_index(index)
    now_dt = dt(now) if now else datetime.now(UTC).replace(microsecond=0)
    selected_days = positive_days(days if days is not None else index["config"]["initial_days"])
    local_date = now_dt.astimezone(ZoneInfo(index["timezone"])).date()
    desired_start = datetime.combine(local_date - timedelta(days=selected_days), time(),
                                     ZoneInfo(index["timezone"])).astimezone(UTC)
    pending = index.get("pending_scan")
    coverage = index["coverage"]
    if pending:
        scan = copy.deepcopy(pending)
    elif not coverage["end"]:
        scan = {"start": iso(desired_start), "end": iso(now_dt), "kind": "initial"}
    elif days is not None and desired_start < dt(coverage["start"]):
        scan = {"start": iso(desired_start), "end": coverage["start"], "kind": "backfill"}
    else:
        if now_dt < dt(coverage["end"]):
            raise ValueError("now precedes the covered cursor")
        start = max(dt(coverage["start"]), dt(coverage["end"]) -
                    timedelta(hours=index["config"]["overlap_hours"]))
        scan = {"start": iso(start), "end": iso(now_dt), "kind": "incremental"}
    start, end = dt(scan["start"]), dt(scan["end"])
    return {
        "account_email": index["account_email"], "index_revision": index["revision"],
        "scan": scan,
        "gmail_query": "in:anywhere -in:drafts after:{} before:{}".format(
            math.floor(start.timestamp()) - 1, math.ceil(end.timestamp())),
        "logical_interval": "start inclusive, end exclusive; filter returned metadata",
        "known_message_ids": sorted(mid for mid, message in index["processed_messages"].items()
                                    if start <= dt(message["received_at"]) < end),
    }


def clean_event(event):
    if event.get("type") not in EVENT_TYPES:
        raise ValueError("Unknown event type: " + str(event.get("type")))
    if not norm(event.get("company")):
        raise ValueError("Application events require an identified company")
    clean = {"company": str(event["company"]).strip(), "type": event["type"],
             "confidence": event.get("confidence", "medium")}
    if clean["confidence"] not in {"high", "medium", "low"}:
        raise ValueError("Invalid event confidence")
    for key in ("title", "requisition_id", "external_job_id", "external_job_source", "location", "cohort"):
        if event.get(key) is not None and str(event[key]).strip():
            clean[key] = str(event[key]).strip()[:500]
    if bool(clean.get("external_job_id")) != bool(clean.get("external_job_source")):
        raise ValueError("External job IDs require both external_job_id and external_job_source")
    if event.get("requisition_id_truncated"):
        clean["requisition_id_truncated"] = True
    if event.get("occurred_at"):
        clean["occurred_at"] = iso(dt(event["occurred_at"]))
    if event.get("excerpt"):
        clean["excerpt"] = str(event["excerpt"])[:500]
    if event.get("related_message_ids"):
        clean["related_message_ids"] = sorted(set(map(str, event["related_message_ids"])))
    if event.get("action"):
        action = event["action"]
        if action.get("state") not in {"requested", "completed", "unknown"}:
            raise ValueError("Action state must be requested, completed, or unknown")
        if not action.get("kind") or not action.get("description"):
            raise ValueError("Action requires kind and description")
        clean["action"] = {key: str(action[key])[:500] for key in
                           ("id", "kind", "description", "deadline", "state") if action.get(key)}
    return clean


def clean_message(message, start, end):
    mid = str(message.get("message_id", "")).strip()
    if not mid:
        raise ValueError("message_id is required")
    received = dt(message["received_at"])
    if not start <= received < end:
        raise ValueError("Message " + mid + " is outside the logical scan interval")
    disposition = message.get("disposition")
    if disposition not in {"application", "excluded", "unresolved"}:
        raise ValueError("Invalid message disposition")
    clean = {"message_id": mid, "received_at": iso(received), "disposition": disposition}
    if message.get("reason"):
        clean["reason"] = str(message["reason"])[:300]
    if disposition == "excluded":
        if message.get("events"):
            raise ValueError("Excluded messages cannot contain application events")
        return clean
    for key in ("thread_id", "subject", "from", "url"):
        if message.get(key):
            clean[key] = str(message[key])[:1000 if key == "url" else 300]
    clean["events"] = [clean_event(event) for event in message.get("events", [])]
    if disposition == "application" and not clean["events"]:
        raise ValueError("Application messages require at least one evidence event")
    return clean


def app_identity(event, message_id, offset):
    company = norm(event["company"])
    if event.get("requisition_id") and not event.get("requisition_id_truncated"):
        kind = "requisition"
        key = company + "|req:" + reqnorm(event["requisition_id"])
    elif event.get("external_job_id") and event.get("external_job_source"):
        kind = "external_job"
        key = company + "|external:" + norm(event["external_job_source"]) + "|" + event["external_job_id"]
    elif event.get("title") and not event.get("requisition_id_truncated"):
        kind = "title"
        key = "|".join((company, "title:" + norm(event["title"]),
                        "location:" + norm(event.get("location")),
                        "cohort:" + norm(event.get("cohort"))))
    else:
        kind = "unresolved"
        key = company + "|unresolved:" + message_id + ":" + str(offset)
    return "app_" + hashlib.sha256(key.encode()).hexdigest()[:20], kind


def derive(index):
    applications = {}
    for mid, message in index["processed_messages"].items():
        for offset, event in enumerate(message.get("events", [])):
            app_id, identity = app_identity(event, mid, offset)
            if app_id not in applications:
                applications[app_id] = {
                    "application_id": app_id, "company": event["company"],
                    "title": event.get("title"), "requisition_id": event.get("requisition_id"),
                    "external_job_id": event.get("external_job_id"),
                    "external_job_source": event.get("external_job_source"),
                    "requisition_id_truncated": event.get("requisition_id_truncated", False),
                    "location": event.get("location"), "cohort": event.get("cohort"),
                    "identity_confidence": identity, "events": [],
                }
            application = applications[app_id]
            for key in ("title", "external_job_id", "external_job_source", "location", "cohort"):
                if not application.get(key) and event.get(key):
                    application[key] = event[key]
            evidence = {**copy.deepcopy(event), "message_id": mid,
                        "received_at": message["received_at"],
                        "occurred_at": event.get("occurred_at", message["received_at"])}
            if message.get("url"):
                evidence["url"] = message["url"]
            application["events"].append(evidence)
    lookups = {"companies": {}, "requisitions": {}, "external_jobs": {}, "titles": {}}
    for app_id, application in applications.items():
        events = sorted(application["events"], key=lambda e: (e["occurred_at"], e["message_id"]))
        status, actions, conflicts = "unknown", {}, []
        status_event = None
        for event in events:
            kind = event["type"]
            if kind == "role_closed" and status in {"rejected", "withdrawn", "offer_accepted", "hired"}:
                pass  # Vacancy state does not erase the candidate's known outcome.
            elif kind in TERMINAL:
                status = kind
                status_event = event
            elif status not in TERMINAL and STAGES.get(kind, -1) > STAGES.get(status, -1):
                status = kind
                status_event = event
            elif status in TERMINAL and kind in STAGES and STAGES[kind] >= STAGES["application_submitted"]:
                conflicts.append({"message_id": event["message_id"], "event": kind,
                                  "reason": "Progress evidence after a terminal outcome; review before reopening"})
            if event.get("action"):
                action = event["action"]
                key = action.get("id") or norm(action["kind"]) + "|" + norm(action["description"])
                if key not in actions or actions[key]["state"] != "completed":
                    actions[key] = {**action, "message_id": event["message_id"],
                                    "received_at": event["received_at"],
                                    "completion_evidence": action["state"] == "completed"}
                    if event.get("url"):
                        actions[key]["url"] = event["url"]
        latest = events[-1]
        latest_response = {key: copy.deepcopy(latest.get(key)) for key in
                           ("type", "occurred_at", "received_at", "confidence", "message_id", "excerpt")}
        for key in ("url", "action"):
            if key in latest:
                latest_response[key] = copy.deepcopy(latest[key])
        application.update({
            "events": events, "status": status,
            "status_confidence": status_event["confidence"] if status_event else None,
            "status_message_id": status_event["message_id"] if status_event else None,
            "latest_response": latest_response,
            "role_closed": any(event["type"] == "role_closed" for event in events),
            "applied_confirmed": any(event["type"] in APPLIED_TYPES and event["confidence"] == "high"
                                     for event in events),
            "actions": list(actions.values()), "conflicts": conflicts,
            "first_evidence_at": min(event["received_at"] for event in events),
            "last_evidence_at": max(event["received_at"] for event in events),
            "evidence_urls": sorted({event["url"] for event in events if event.get("url")}),
            "external_job_aliases": [{"external_job_source": source, "external_job_id": job_id}
                                     for source, job_id in sorted({
                                         (norm(event["external_job_source"]), event["external_job_id"])
                                         for event in events if event.get("external_job_id")})],
        })
        company = norm(application["company"])
        lookups["companies"].setdefault(company, []).append(app_id)
        if application["identity_confidence"] == "requisition":
            lookups["requisitions"].setdefault(company + "|" + reqnorm(application["requisition_id"]), []).append(app_id)
        if application.get("title"):
            lookups["titles"].setdefault(company + "|" + norm(application["title"]), []).append(app_id)
        for alias in application["external_job_aliases"]:
            key = company + "|" + alias["external_job_source"] + "|" + alias["external_job_id"]
            lookups["external_jobs"].setdefault(key, []).append(app_id)
    index["applications"] = dict(sorted(applications.items()))
    index["lookup"] = {kind: {key: sorted(ids) for key, ids in sorted(values.items())}
                       for kind, values in lookups.items()}


def merge_coverage(index, start, end):
    coverage = index["coverage"]
    segments = [(dt(item["start"]), dt(item["end"])) for item in coverage["segments"]]
    segments.append((start, end))
    merged = []
    for left, right in sorted(segments):
        if merged and left <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(right, merged[-1][1]))
        else:
            merged.append((left, right))
    anchor = dt(coverage["end"]) if coverage["end"] else end
    main = next((interval for interval in merged if interval[0] <= anchor <= interval[1]), merged[0])
    coverage.update({"start": iso(main[0]), "end": iso(main[1]),
                     "segments": [{"start": iso(left), "end": iso(right)} for left, right in merged]})


def ingest(index, batch):
    """Deduplicate classified mail and commit a complete interval, or a checkpoint."""
    check_index(index)
    if account(batch.get("account_email")) != index["account_email"]:
        raise ValueError("Account mismatch; use a separate index")
    scan = batch["scan"]
    start, end = dt(scan["start"]), dt(scan["end"])
    if start >= end:
        raise ValueError("Scan start must precede end")
    if not isinstance(scan.get("complete"), bool):
        raise ValueError("scan.complete must explicitly be true or false")
    pending = index.get("pending_scan")
    same_pending = pending and dt(pending["start"]) == start and dt(pending["end"]) == end
    if pending and not same_pending:
        raise ValueError("Finish or explicitly resolve the existing pending scan first")
    result = copy.deepcopy(index)
    for raw in batch.get("messages", []):
        message = clean_message(raw, start, end)
        mid = message["message_id"]
        existing = result["processed_messages"].get(mid)
        if existing and existing != message:
            raise ValueError("Conflicting classification for message " + mid + "; review evidence instead of overwriting")
        result["processed_messages"][mid] = message
    if scan["complete"]:
        merge_coverage(result, start, end)
        result["pending_scan"] = None
    else:
        result["pending_scan"] = {"start": iso(start), "end": iso(end)}
        for key in ("kind", "next_page_token"):
            if scan.get(key) is not None:
                result["pending_scan"][key] = scan[key]
    derive(result)
    if result != index:
        result["revision"] = index["revision"] + 1
    return result


def correct(index, replacement_message, reason, evidence_ids):
    """Explicitly enrich a prior classification using already indexed evidence."""
    check_index(index)
    mid = str(replacement_message.get("message_id", ""))
    previous = index["processed_messages"].get(mid)
    if not previous:
        raise ValueError("Corrections require an existing processed message")
    if dt(replacement_message["received_at"]) != dt(previous["received_at"]):
        raise ValueError("A correction cannot change the received timestamp")
    if not str(reason or "").strip():
        raise ValueError("A correction requires an explicit reason")
    evidence_ids = sorted(set(map(str, evidence_ids)))
    if not evidence_ids or mid in evidence_ids:
        raise ValueError("Provide distinct corroborating processed message IDs")
    evidence = []
    for evidence_id in evidence_ids:
        source = index["processed_messages"].get(evidence_id)
        if not source or not source.get("events"):
            raise ValueError("Corroboration must reference indexed application evidence")
        evidence.extend(source["events"])
    for key in ("thread_id", "subject", "from", "url"):
        if previous.get(key) and replacement_message.get(key, previous[key]) != previous[key]:
            raise ValueError("A correction cannot rewrite source metadata: " + key)
    received = dt(previous["received_at"])
    replacement = clean_message({**previous, **replacement_message}, received, received + timedelta(seconds=1))
    old_companies = {norm(event["company"]) for event in previous.get("events", [])}
    if not replacement.get("events") or not old_companies:
        raise ValueError("This narrow correction requires an existing company-linked classification")

    def corroborates(event, proof):
        if norm(event["company"]) != norm(proof["company"]):
            return False
        if event.get("requisition_id") and not event.get("requisition_id_truncated"):
            return (not proof.get("requisition_id_truncated") and
                    reqnorm(event["requisition_id"]) == reqnorm(proof.get("requisition_id")))
        if event.get("external_job_id"):
            return (norm(event["external_job_source"]) == norm(proof.get("external_job_source")) and
                    event["external_job_id"] == proof.get("external_job_id"))
        return bool(event.get("title") and norm(event["title"]) == norm(proof.get("title")))

    for event in replacement["events"]:
        if norm(event["company"]) not in old_companies or not any(corroborates(event, proof) for proof in evidence):
            raise ValueError("Corroborating evidence does not support the replacement company and job identity")
        for old in previous.get("events", []):
            if norm(old["company"]) == norm(event["company"]) and old.get("requisition_id"):
                old_req, new_req = reqnorm(old["requisition_id"]), reqnorm(event.get("requisition_id"))
                if old.get("requisition_id_truncated"):
                    if not new_req.startswith(old_req):
                        raise ValueError("The full requisition does not extend the prior truncated ID")
                elif old_req != new_req:
                    raise ValueError("A correction cannot retarget a known full requisition")
    if replacement == previous:
        return copy.deepcopy(index)
    result = copy.deepcopy(index)
    result["revision"] += 1
    result["processed_messages"][mid] = replacement
    result.setdefault("correction_history", []).append({
        "revision": result["revision"], "corrected_at": iso(datetime.now(UTC)),
        "message_id": mid, "reason": str(reason).strip(), "evidence_message_ids": evidence_ids,
        "previous_classification": copy.deepcopy(previous),
        "replacement_classification": copy.deepcopy(replacement),
    })
    derive(result)
    return result


def lookup(index, company, title=None, requisition_id=None, external_job_id=None, external_job_source=None):
    check_index(index)
    if bool(external_job_id) != bool(external_job_source):
        raise ValueError("External job lookup requires both its ID and source")
    if requisition_id and external_job_id:
        raise ValueError("Query an employer requisition or an external job ID separately")
    candidates = [index["applications"][key] for key in
                  index["lookup"]["companies"].get(norm(company), [])]
    exact, possible = [], []
    other_requisitions = []
    for application in candidates:
        kind = application["identity_confidence"]
        if requisition_id:
            if kind == "requisition":
                if reqnorm(application["requisition_id"]) == reqnorm(requisition_id):
                    exact.append(application)
                else:
                    other_requisitions.append(application["requisition_id"])
            elif not title or not application.get("title") or norm(application["title"]) == norm(title):
                possible.append(application)
        elif external_job_id:
            aliases = application.get("external_job_aliases", [])
            if any(alias["external_job_id"] == str(external_job_id) and
                   norm(alias["external_job_source"]) == norm(external_job_source) for alias in aliases):
                exact.append(application)
            elif not aliases and (not title or not application.get("title") or norm(application["title"]) == norm(title)):
                possible.append(application)
        elif title:
            if application.get("title") and norm(application["title"]) == norm(title) and kind != "unresolved":
                exact.append(application)
            elif not application.get("title") or norm(application["title"]) == norm(title):
                possible.append(application)
        else:
            exact.append(application)
    matches = exact if exact else possible
    ambiguous_identity = bool((external_job_id or title) and not requisition_id and len(exact) > 1)
    return {
        "match": "possible" if ambiguous_identity else "exact" if exact else "possible" if possible else "no_evidence",
        "query_scope": "requisition" if requisition_id else "external_job" if external_job_id else "title" if title else "company",
        "identity_ambiguous": ambiguous_identity,
        "applied_confirmed": bool(exact) and not ambiguous_identity and any(app["applied_confirmed"] for app in exact),
        "applications": sorted(matches, key=lambda app: app["last_evidence_at"], reverse=True),
        "possible_candidates": sorted(possible, key=lambda app: app["last_evidence_at"], reverse=True),
        "other_known_requisitions": sorted(set(other_requisitions)),
        "coverage": copy.deepcopy(index["coverage"]),
        "pending_scan": copy.deepcopy(index["pending_scan"]),
        "qualification": "No evidence means no matching evidence in the indexed coverage; it does not prove no application was sent.",
        "action_qualification": "A requested action records a notification; current completion is unknown unless completion evidence is indexed.",
    }


def summary(index):
    check_index(index)
    status_counts = {}
    for application in index["applications"].values():
        status_counts[application["status"]] = status_counts.get(application["status"], 0) + 1
    dispositions = {}
    for message in index["processed_messages"].values():
        dispositions[message["disposition"]] = dispositions.get(message["disposition"], 0) + 1
    return {
        "account_email": index["account_email"], "revision": index["revision"],
        "coverage": index["coverage"], "pending_scan": index["pending_scan"],
        "processed_messages": len(index["processed_messages"]),
        "message_dispositions": dispositions, "applications": len(index["applications"]),
        "unresolved_identities": sum(app["identity_confidence"] == "unresolved"
                                     for app in index["applications"].values()),
        "status_counts": status_counts,
    }


def load_index(path):
    with open(path, encoding="utf-8") as handle:
        index = json.load(handle)
    check_index(index)
    return index


def save_index(path, index, expected_revision):
    """Local atomic compare-and-swap. Cloud callers also need storage version CAS."""
    path = Path(path)
    check_index(index)
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = path.with_name(path.name + ".lock")
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as error:
        raise ValueError("Index is locked by another writer; retry after that writer finishes") from error
    temporary = None
    try:
        with os.fdopen(descriptor, "w") as handle:
            handle.write(str(os.getpid()))
        if path.exists():
            current = load_index(path)
            if expected_revision is None or current["revision"] != expected_revision:
                raise ValueError("Revision conflict; reload the current index and reapply the batch")
            if current["account_email"] != index["account_email"]:
                raise ValueError("Cannot replace an index for a different account")
        elif expected_revision is not None:
            raise ValueError("Expected an existing index, but none was found")
        descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(index, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)
        lock.unlink(missing_ok=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="Create a new account-specific index")
    init.add_argument("--account", required=True)
    init.add_argument("--days", type=int, default=60)
    init.add_argument("--timezone", default="America/Halifax")
    planner = commands.add_parser("plan", help="Plan an immutable incremental or backfill window")
    planner.add_argument("--now", help="UTC or offset ISO timestamp; defaults to current UTC")
    planner.add_argument("--days", type=int, help="Explicitly extend initial history to this many calendar days")
    ingestion = commands.add_parser("ingest", help="Commit classified evidence and scan progress")
    ingestion.add_argument("--batch", required=True)
    ingestion.add_argument("--expected-revision", required=True, type=int)
    correction = commands.add_parser("correct", help="Audited identity enrichment using indexed corroborating evidence")
    correction.add_argument("--message", required=True, help="Replacement classified message JSON")
    correction.add_argument("--reason", required=True)
    correction.add_argument("--evidence-id", action="append", required=True, help="Processed corroborating message ID; repeatable")
    correction.add_argument("--expected-revision", required=True, type=int)
    search = commands.add_parser("lookup", help="Find evidence for a company, title, or exact requisition")
    search.add_argument("--company", required=True)
    search.add_argument("--title")
    search.add_argument("--requisition", "--requisition-id", dest="requisition_id")
    search.add_argument("--external-job-id")
    search.add_argument("--external-job-source")
    commands.add_parser("summary", help="Show coverage and compact index counts")
    for command in commands.choices.values():
        command.add_argument("--index", required=True, help="Durable JSON path or materialized cloud file")
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            index = new_index(args.account, args.days, args.timezone)
            save_index(args.index, index, expected_revision=None)
            output = summary(index)
        else:
            index = load_index(args.index)
            if args.command == "plan":
                output = plan(index, args.now, args.days)
            elif args.command == "ingest":
                if index["revision"] != args.expected_revision:
                    raise ValueError("Revision conflict before ingest; reload before retrying")
                with open(args.batch, encoding="utf-8") as handle:
                    updated = ingest(index, json.load(handle))
                save_index(args.index, updated, expected_revision=args.expected_revision)
                output = summary(updated)
            elif args.command == "correct":
                if index["revision"] != args.expected_revision:
                    raise ValueError("Revision conflict before correction; reload before retrying")
                with open(args.message, encoding="utf-8") as handle:
                    updated = correct(index, json.load(handle), args.reason, args.evidence_id)
                save_index(args.index, updated, expected_revision=args.expected_revision)
                output = summary(updated)
            elif args.command == "lookup":
                output = lookup(index, args.company, args.title, args.requisition_id,
                                args.external_job_id, args.external_job_source)
            else:
                output = summary(index)
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
