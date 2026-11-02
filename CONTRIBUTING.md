# Contributing

Thank you for helping! This is a small, practical tool, and the most valuable contributions are
**real-world findings about how EUDAMED behaves** and **tests that make the generator safer**.

## Before you start

* Read [`docs/development.md`](docs/development.md) - it explains the single-file architecture and the
  pitfalls of editing it.
* Run the tests: `pip install -r requirements-dev.txt && python -m unittest discover -s tests -v`.
  Run them after *every* change to the HTML file: a single stray line break in a JavaScript string silently
  breaks the whole page.

## Never publish real data

Issues, pull requests, test fixtures and screenshots must **not** contain real device data, SRNs, certificate
numbers, Notified Body numbers, product or company names, access tokens, or complete acknowledgement files
from the portal. Replace identifiers by obviously fake ones (`+EXAMPLE000011X`, `DE-MF-000000000`, `0000`).
The repository tests refuse data files and e-mail addresses, but they cannot recognise every real identifier -
please check your own changes.

## Reporting a portal behaviour

The best bug reports for this project are anonymised acknowledgements. Please include:

1. which portal upload mechanism you used and the `serviceID`/`serviceOperation` in your file,
2. the `responseCode`, `operationErrorCode` and `operationErrorDetail` (identifiers replaced),
3. what you expected, and what you changed to make it work (if you did).

If it is a new rule, see "The self-check" in the development guide: a rule belongs in the generator's
self-check, in `tools/check_xml.py`, in a test, and in `docs/eudamed-portal-rules.md` with its evidence level.

## Pull requests

* Keep changes focused; one topic per pull request.
* Add or update tests and the `[Unreleased]` section of `CHANGELOG.md`.
* The interface is bilingual: every new user-visible text needs an English **and** a German string.
* Do not add network requests, web fonts, analytics or any external resource - the "runs entirely locally"
  promise is tested.
* New third-party code needs a compatible license and an entry in `THIRD_PARTY_NOTICES.md`.

By contributing you agree that your contribution is licensed under the project's MIT license.
