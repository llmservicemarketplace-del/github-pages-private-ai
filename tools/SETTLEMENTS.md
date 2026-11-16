# Settlement directory monitoring

The default view is accepting new claims. Automatic payments, existing-claim follow-up, upcoming programs, closed claims, and listings needing verification are separate categories. No receipt required is a reviewed property of a particular benefit, not a synonym for no eligibility requirements.

The daily GitHub Actions job reads the source registry, checks published official notices, discovers directory links, deduplicates official URLs, and stores unconfirmed leads in data/settlement-review-queue.json. Registry status and last-success dates are public. Official administrator pages override discovery-directory dates. Robots restrictions and source failures are retained as visible failures, not successful checks.

New directory leads are published as submission-route-checked only after the official page has a claim link and an explicit matching future claim deadline. Their eligibility, state restrictions, and proof requirements remain unknown, visibly labeled, and excluded from the no-receipt filter. Other leads await editorial review. Manually reviewed notice changes require renewed review. Missing or failed checks remove listings from the default view; stale checks age out after seven days. This is monitoring of configured sources, not exhaustive coverage of every settlement or automatic legal review.

Contact profiles, preparation HTML, GoodRx official PDF integrity checks, optional donations, and the application organizer are preserved. Downloaded worksheets are not official submissions. No signatures, declarations, or payment accounts are filled automatically.

Run: pip install -r tools/requirements-settlements.txt; python -m unittest discover -s tests/settlements; node tests/settlements/core.test.cjs; python tools/update_settlements.py. Use --render-only to rebuild embedded/static listings without fetching.

To add a source, supply id, name, kind and HTTPS url in data/settlement-sources.json. Supported kinds: classaction, ftc, cfpb, directory (path_pattern), government. Adding a source does not validate its discoveries. Source-layout changes can require parser maintenance.
