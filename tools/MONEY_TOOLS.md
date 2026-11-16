# Private Money Help tools
- application-organizer.html: manual records, document checklists, self-entered deadlines and statuses.
- unclaimed-money-tool.html: state links, local notes, and a preparation worksheet; never a replacement state claim form.
- billing-dispute-letter.html: user-reviewed factual letter drafts, downloadable HTML/text, manual email composition.

All tools use assets/money-tools/common.js and optional shared contact profile nfccop.settlement.profile.v1.
Without device opt-in, sessionStorage keeps data in the current tab. With opt-in, localStorage is used.
Storage is not encrypted. Exported backups use PBKDF2-SHA256 (250k iterations), random 16-byte salts, AES-256-GCM, random 12-byte IVs.
Backups include contact profile and records. Passwords are neither saved nor recoverable. Imported data is schema-normalized, limited to 500 records, and escaped on display.
No document upload, automatic submission, email sending, or closed-page notification service exists.
Do not add analytics or send profile, notes, letter text, or imported data to external services.
Only public catalog/state/settlement JSON is fetched. Email drafts are opened only on an explicit user click.

State links are sourced from https://unclaimed.org/search/ and refreshed by update-unclaimed-directory.yml.
Reject incomplete state refreshes; keep the last known file on failure.
data/money-programs.json indexes existing Money Help guides. Document lists are generic planning aids unless specifically reviewed.
The shared button-conversions.js adds a public-guide organizer link without personal URL parameters.
The settlement finder offers per-settlement organizer links and shares the optional/session contact profile.

Check: node tests/money-tools/core.test.cjs
Refresh: python tools/update_unclaimed_directory.py
Review financial/legal guidance against official FTC/CFPB and state sources when changing it.
Never imply that a saved status proves an agency submitted or approved anything.
