# Settlement and refund directory
Page: /money-help/settlements-and-refunds.html
Data: data/settlements.json. Frontend has no profile submission endpoint.
Daily updater: .github/workflows/update-settlements.yml, 11:23 UTC, plus manual dispatch.

## Editorial workflow
Use directories only to find leads. Add a settlement only after reviewing its official notice/form.
Record eligibility, receipt and notice-ID requirements separately; use null for unknown.
Use deadline_at only for a verified timezone-specific deadline. Never invent a closing time.
Set review_status=verified and last_verified after human review.
Hash the reviewed official source using normalized() in tools/update_settlements.py. For a PDF hash exact bytes.
Do not run --bootstrap on existing changed sources to bypass review.
The updater pauses supported PDF generation if a reviewed source changes. A failed source check does not advance last_checked. Templates also stop after seven days without a successful check.
FTC discovery publishes only links/titles from the official FTC table with no invented payout or eligibility.
New non-FTC settlements require editorial review; automated monitoring cannot certify eligibility.
Do not label a listed email as an accepted claim route unless the official instructions explicitly allow email claims. submission_email is otherwise omitted.
The local profile contains contact details only and is stored only with the visitor's opt-in.
Never add profile values to URLs, analytics, logging, or a backend. Downloads remain the visitor's responsibility.

## Official PDF templates
GoodRx's unmodified two-page official blank is stored in assets/settlements/forms/goodrx-official.pdf.
Source URL and SHA-256 are recorded in the data. Only contact fields are added as editable widgets.
Payment choices, declarations, signature and date stay blank. The mailed form requires personal review and completion.
Do not substitute an NFCcop worksheet for an official claim.
Check any new template visually with long and accented names. Keep official instructions intact.

## Update & test
python -m unittest discover -s tests/settlements -p 'test_*.py'
node tests/settlements/core.test.cjs
python tools/update_settlements.py
The workflow commits feed changes and requests a GitHub Pages rebuild. Inspect failed Actions runs.
pdf-lib 1.17.1 is vendored locally (MIT license) to avoid loading third-party code while a visitor types.
