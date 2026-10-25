---
name: resume-pdf-validator
description: Tailor an existing resume to a specific role using verified evidence, then validate its exported PDF for factual accuracy, page count, selectable text, ATS reading order, layout bounds, and relevant terms. Use when preparing or checking a resume; do not invent credentials or generate filler.
---

# Resume PDF Validator

Create a role-specific resume from the candidate's current source material and validate the exported document. Preserve the original resume and work in a new, clearly named output location. Follow any user-provided page limit, template, regional conventions, and required output format.

## Inputs

- Complete, current job description and employer URL.
- Current resume source and authoritative evidence for dates, roles, projects, technologies, and outcomes.
- The requested page count, target role, and existing document template.
- A PDF reader, text extractor, and page renderer when available.

Treat the PDF baseline as a document, not as authority over newer user-provided facts. If claims cannot be traced to a source, omit them or flag them for clarification.

## Workflow

1. Extract the role's responsibilities, required and preferred qualifications, seniority, education, and repeated technical terms from the full posting. Record the employer URL and date checked.
2. Select evidence relevant to those needs. Preserve the individual's contribution boundary, employment dates, and implementation status. Distinguish production, tested, prototype, planned, and unverified work. Keep measurement conditions and comparison baselines with any metric.
3. Tailor the existing resume source and layout. Reorder or remove content to improve relevance. Do not add generic filler, unsupported keywords, hidden text, or claims inferred from the job description.
4. Compile or export the PDF. Confirm the requested number of pages and expected page dimensions. Extract text and inspect its order, contact fields, dates, headings, links, and important role terminology.
5. Check every text box or word against page bounds. Where tools permit, detect overlaps and render each page for visual inspection. Inspect top and bottom margins, clipping, line wraps, orphaned headings, glyph substitutions, and crowded or unusually empty regions.
6. Compare substantive statements to the evidence sources. Verify that job-specific wording remains accurate, no stale company or role text remains, and every included metric retains its scope and conditions.
7. Report each validation as `pass`, `fail`, or `not checked`, with the tool or method used. Fix failures and rerun only the affected checks; a rendered screenshot does not establish selectable text and text extraction does not establish visual quality.

## Output

Provide the resume source and final PDF, requested page count, extracted-text result, layout and visual findings, role-term findings, factual review, and unresolved limitations. Keep the original source unchanged. Do not submit forms or upload the resume unless the user separately authorizes that action.

## Example

> Tailor this existing resume for the attached junior API role using only the supplied evidence. Keep it to one page. Export a PDF, then report page count, selectable-text and reading-order checks, page bounds, clipping or overlap, role terms, and any claims that could not be verified. Do not add filler or overwrite the source resume.

Supply a synthetic profile and posting if you want to exercise the workflow without real personal information.

## Verification and limits

Page count and text extraction are mechanically testable; factual relevance and visual quality need human review. Bounds and overlap scripts can miss complex glyph clipping, occlusion, or reading-order problems. State when a tool was unavailable and use an appropriate fallback without claiming that the skipped check passed. A validated PDF does not establish employer acceptance or ATS ranking.
