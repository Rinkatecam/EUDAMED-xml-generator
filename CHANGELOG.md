# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Two version numbers exist and are deliberately kept separate:

* **Application version** (this changelog, the `VERSION` file, git tags `vX.Y.Z`) - SemVer for the tool itself.
* **Schema version** (`SCHEMA_VERSION` in the application) - the EUDAMED DTX XSD version the generated
  messages declare. EUDAMED pins it with a fixed attribute, so a new schema drop normally means a new
  release of this tool.

## [Unreleased]

### Documentation
- `UDI_DI.POST` messages (UDI-DIs added to an existing Basic UDI-DI) are now documented as confirmed to be
  accepted by the live portal (status as of 2026-11). The 1.0.0 notes below describe the state at release time.

## [1.0.0] - 2026-11-02

First public release.

### Added
- Browser-based generator (single HTML file, runs fully offline, no installation) that turns an Excel
  workbook (`DEVICES`, `MARKET_INFO`, `SUBSTANCES`, `STORAGE AND HANDLING`) into EUDAMED DTX `Push`
  messages for MDR devices, targeting XSD schema **3.0.30**.
- Bilingual (EN/DE) interface and a formatted Excel template with drop-down lists, per-column help
  and a legend.
- Validation with a correction worklist that points to the exact cells, structural pre-flight checks
  (missing/renamed sheets and columns) and a warning sign-off step.
- **Two-message upload model**: exactly one `DEVICE.POST` row per new Basic UDI-DI family (creates it) and
  `UDI_DI.POST` messages (`device:UDIDIData`) for every other UDI-DI, because EUDAMED lets a Basic UDI-DI
  be created only once. Basic UDI-DIs that already exist can be flagged so their whole family is
  generated as `UDI_DI.POST` only.
- Output self-check that aborts generation instead of producing files the portal is known to reject:
  schema version pin, service/payload agreement, one entity type per message, the 300-entity limit and
  the language rules for comment texts.
- ZIP output with `UPLOAD_INSTRUCTIONS.txt`, a human- and machine-readable submission record with
  SHA-256 hashes, and a resubmission mode for selected UDI-DIs.
- Support for the optional schema 3.0.30 fields: authorised representative SRN, device name (`modelName`),
  `IIb_implantable_exceptions` and a secondary identifier.
- `tools/check_xml.py`: independent checker for DTX messages (portal rules, optional XSD validation).
- Test suite (syntax, version consistency, repository hygiene, template/schema consistency, rule checker).
- Documentation of EUDAMED behaviour that the XSD does not express (`docs/eudamed-portal-rules.md`).

### Changed
- No external resources are requested any more (web fonts removed; system fonts are used).

### Known limitations
- MDR devices only; services `DEVICE.POST` and `UDI_DI.POST` only.
- The application JavaScript is checked for syntax and consistency in CI but is not yet executed by
  automated tests (see `docs/development.md`).
- The `UDI_DI.POST` message shape is validated against the XSD; confirmation against a live portal
  acknowledgement is welcome (please open an issue with an anonymised response).

[Unreleased]: ../../compare/v1.0.0...HEAD
[1.0.0]: ../../releases/tag/v1.0.0
