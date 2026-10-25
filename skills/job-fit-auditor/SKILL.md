---
name: job-fit-auditor
description: Compare a candidate's documented evidence with current job requirements, flag eligibility and experience gaps, and produce a traceable fit ranking. Use for job-posting audits and shortlists; not for submitting applications or predicting hiring outcomes.
---

# Job Fit Auditor

Assess how a specific candidate's supplied evidence matches a specific, current job posting. Treat employer requirements as the source of role criteria and the candidate's cited records as the source of qualifications. Job-board labels and recommender scores are discovery clues only.

## Inputs

- The complete posting, preferably from the employer's application page, with URL and retrieval date.
- The candidate's current profile and source-backed experience records.
- The user's target locations, work authorization, availability, salary floor, preferred role level, and any application-history records.
- If ranking multiple roles, the ranking dimensions or weights. If none are supplied, compare dimensions in a table and do not invent a precise composite score.

If an input is absent, mark it unknown. Do not infer personal characteristics, work authorization, availability, compensation, or experience from a name, location, graduation year, or platform badge.

## Workflow

1. Verify that the requisition is still open and capture the complete description, employer URL, title, location, posting date if shown, and requisition ID. Prefer the employer page. If only a partial or stale copy is available, label verification incomplete.
2. Normalize the requirements into distinct items. Mark each as mandatory, preferred, responsibility, or unclear. Record the source passage or heading for each item. Keep years of experience separate from technology requirements and distinguish professional, internship, academic, and personal-project evidence.
3. Map each item to the strongest candidate source. Use `direct`, `transferable`, `not shown`, or `unclear`; cite the source and explain the match briefly. Do not turn adjacent tools, prototypes, or planned work into direct experience.
4. Check gates before ranking: work authorization, geography, employment type, start-date compatibility, required credentials or language, salary floor where stated, experience level, and any mandatory requirement with no credible evidence. A preferred qualification alone is not a rejection reason.
5. Check prior-application history. Match by requisition ID when available; otherwise compare employer and role while noting uncertainty. A draft is not proof of submission. Preserve applied, rejected, and withdrawn records. Do not treat a similar title with a different requisition as the same vacancy without evidence.
6. Score only after evidence mapping. Use the user's supplied formula. If there is no formula, provide dimension ratings and a reasoned rank without made-up weights. Show unknowns and gating flags beside any composite. Treat platform match labels, applicant counts, alumni signals, and application method as metadata, never as hiring probability.
7. Recommend, hold, or reject each role with reasons. Explain unsupported mandatory requirements and uncertain salary, eligibility, location, history, or start date. Link every current posting.

## Output

For each role, report the employer, title, requisition, current posting URL and check date; status of the posting; fit evidence and gaps; location, salary, level, and availability flags; history and duplicate findings; score or dimension ratings; and a concise decision. Keep a source list so another reviewer can reproduce the assessment.

## Example

See [the fictional job-fit example](../../examples/fictional-job-fit.md). It demonstrates a direct match, a transferable match, and a missing requirement without representing a real candidate or vacancy.

## Verification and limits

Reopen the employer posting before a consequential shortlist or application. Recheck duplicated requisitions and history against the available tracker. An inaccessible employer page is a verification gap, not proof that a posting is closed. A fit score is a structured comparison against supplied evidence, not a probability of interview or offer. Final eligibility and application decisions belong to the candidate.
