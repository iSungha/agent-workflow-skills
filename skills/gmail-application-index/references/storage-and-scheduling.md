# Persistence, commands, and scheduling

## One portable canonical index

JSON is the durable source of truth: account/configuration, completed coverage intervals, pending scan, processed IDs, evidence/events, and derived application/lookup maps. No mailbox credentials or user data belong in the skill package. Gmail and Library access stay with authenticated runtime tools; the helper only transforms local data.

Cloud: follow the current Library skill to resolve, materialize, create, or replace `Gmail_Application_Index.json`. Resolve an existing identity and verify its account before creating a new file. Preserve its exact `library_file_id` and version. Keep the ID in the task prompt or durable configuration, not a temporary path. Replace the same file with the concrete `expected_current_version` when available, and follow Library's metadata writeback requirements.

On version conflict, fetch the current file/version and replay the original batch through the helper. Message-ID deduplication makes replay safe. Save with the new expected version; after three conflicts, report unsaved work. Never merge coverage by taking minimum/maximum across a gap. Only complete intervals count. The helper's local revision guard does not replace storage version checking.

Codex: use the same Library file when connected, otherwise a user-selected persistent local path outside the skill repository. Python 3.9+ with IANA timezone data is required (Windows may need `tzdata`). Offline lookups must show last completed coverage. Cloud and local copies are not automatically synchronized unless they share durable storage or an explicit transfer occurred.

## Command sequence

Substitute observed values and quote paths. Resolve the helper from its current installed folder.

```bash
python3 "$skill_dir/scripts/application_index.py" init --index "$index_path" --account "$account_email" --days 60 --timezone America/Halifax
python3 "$skill_dir/scripts/application_index.py" plan --index "$index_path" --now 2026-10-28T21:24:26Z
# Retrieve and classify Gmail into an account-bound batch.
python3 "$skill_dir/scripts/application_index.py" ingest --index "$index_path" --batch "$batch_path" --expected-revision 0
python3 "$skill_dir/scripts/application_index.py" lookup --index "$index_path" --company ExampleCo --requisition A200
python3 "$skill_dir/scripts/application_index.py" lookup --index "$index_path" --company ExampleCo --external-job-source linkedin --external-job-id 1234567890
python3 "$skill_dir/scripts/application_index.py" summary --index "$index_path"
```

These are illustrative, not user configuration. Use current clock/account/timezone and actual revision. `init` is for a missing file only. `plan --days N` requests earlier coverage without deleting records. After backfill, request the next delta plan until the requested older boundary and current cutoff are covered.

## Complete Gmail enumeration

Use the Gmail message-ID search, not summary results, as authoritative enumeration. Summary search has been observed to omit IDs even when an ID page lists them. For unseen IDs, obtain summaries/metadata and reconcile against the enumerated set. Fetch every missing summary with read/batch-read. Full bodies are needed only for candidate/uncertain application mail. If only a full-message batch-read tool exists, use it for the missing IDs and retain minimal fields.

Read all pages using actual returned continuation tokens. Labels, keyword searches, and counts are useful filters but cannot prove full-window coverage. A tool timeout or missing message leaves the scan incomplete unless deletion/unavailability is explicitly accounted for as a reported coverage limitation.

## Ingestion contract

UTF-8 JSON, timezone-aware ISO 8601 timestamps. Scan bounds are `[start, end)`. The query should include the start boundary (strict `after:` needs an earlier second); filter extra metadata to the logical interval. Normalize provider epoch seconds/milliseconds explicitly.

```json
{
  "account_email": "person@example.com",
  "scan": {
    "start": "2026-08-29T03:00:00Z",
    "end": "2026-10-28T21:24:26Z",
    "complete": true,
    "next_page_token": null
  },
  "messages": [
    {
      "message_id": "provider-message-id",
      "thread_id": "provider-thread-id",
      "received_at": "2026-10-28T17:37:00Z",
      "subject": "Application received",
      "from": "careers@example.com",
      "url": "https://mail.google.com/mail/u/0/#all/provider-message-id",
      "disposition": "application",
      "events": [
        {
          "company": "ExampleCo",
          "title": "Graduate Software Engineer 2027",
          "requisition_id": "A200",
          "type": "application_submitted",
          "occurred_at": "2026-10-28T17:37:00Z",
          "excerpt": "We received your application for Graduate Software Engineer 2027 (A200).",
          "confidence": "high"
        }
      ]
    },
    {
      "message_id": "excluded-message-id",
      "received_at": "2026-10-28T18:00:00Z",
      "disposition": "excluded",
      "reason": "generic job alert"
    }
  ]
}
```

Optional event fields: `requisition_id_truncated` (boolean), the paired `external_job_id`/`external_job_source` (such as a LinkedIn posting ID with source `linkedin`), `location`, `cohort`, `related_message_ids` (corroborating source IDs), and `action` with `kind`, `description`, optional stable `id`, optional `deadline`, and `state`. Reuse a known action ID for a request and its explicit completion even when wording changes; keep separate rounds/tasks distinct. Event types and meanings are in [events-and-matching.md](events-and-matching.md). Message disposition is `application`, `excluded`, or `unresolved`. Excluded mail has no application events.

If retrieval fails, save classified messages with `complete: false` and the actual continuation token if known. Resume identical bounds. If token expires or a message within the last page failed classification, replay the fixed window from the beginning and deduplicate. Never invent a token. Classify every previously unclassified ID before completing coverage.

## Resolve later corroboration

Ordinary `ingest` rejects a changed classification for an existing ID. When new mail clearly resolves an earlier ambiguous receipt, first ingest the new corroborating evidence. Inspect the exact record and `possible_candidates`, then prepare a replacement for the original classified message. Preserve its message ID, received time, source metadata, and original excerpt; add the established identity and related source IDs. Run:

```bash
python3 "$skill_dir/scripts/application_index.py" correct --index "$index_path" --message "$replacement_message_path" --reason "Later task email supplies the full requisition for the same distinctive role" --evidence-id "$corroborating_message_id" --expected-revision "$current_revision"
```

`--evidence-id` is repeatable. The helper requires processed corroborating evidence for the same employer and exact new identity, preserves before/after classifications in `correction_history`, and leaves coverage unchanged. It cannot retarget a known full requisition. It validates structural evidence relationships; the assistant must still establish that the actual text refers to the same application. If corroboration is insufficient, retain the ambiguity. Persist the resulting file with its Library version guard as usual.

## Efficient answers

The first scan examines metadata for the chosen window. Later scans enumerate only the new interval plus 48 hours of overlap and fetch only unseen candidate bodies. Excluded IDs remain processed so alerts are not repeatedly classified.

Use `lookup` output, not the whole file in context. Read source mail again only when cached evidence cannot resolve the question, the user requests it, or an explicit classification correction is needed. An exact identity match is not itself proof of submission: an exact recruiter-contact record still does not mean applied.

For no evidence, include the coverage window. Offer earlier backfill if appropriate. Mail imported later with an old timestamp needs bounded reconciliation; do not claim History API or zero-metadata-read behavior.

## Scheduled task template

Reuse a relevant application-update task and preserve its useful intent. Use 7 a.m. with the user's observed IANA timezone for DST handling; omit unrelated fields in updates. Do not use shell cron or a long-running process in a transient workspace.

Fill the following with observed identities:

> Use $gmail-application-index to refresh the application index for [account], stored as [exact durable file ID]. Load the index and finish any pending scan, then enumerate unseen messages in its next planned window including bounded metadata overlap. Reconcile all enumerated IDs; classify receipts/responses with evidence, update statuses/actions, and persist the same index with version checking. Do not rebuild full history, rely only on labels, or switch accounts. Report new interviews, assessments, recruiter replies, decisions, and explicit deadlines with employer, role, status, action or uncertainty, date, and email link. Exclude generic alerts/marketing. If nothing meaningful changed, say so briefly. If retrieval or saving fails, state last completed coverage and the failure; never claim success.

Only claim daily refresh after the tool confirms an enabled task with the intended schedule/timezone. Runs need Gmail read access, the installed skill, helper execution, and a persistent writer. If a dependency is unavailable, provide cached evidence with its freshness limit or a clear setup limitation.
