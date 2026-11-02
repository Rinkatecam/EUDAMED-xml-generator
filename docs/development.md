# Development guide

## Architecture in one paragraph

The whole application is **one self-contained HTML file** (`eudamed-xml-generator.html`): markup, styles,
the third-party libraries (inlined, see `THIRD_PARTY_NOTICES.md`), the application code and the Excel
template (embedded as base64) are all in it. That is a deliberate choice - users can download one file, open
it, and work offline - but it shapes how you edit the project.

The application code is organised in numbered modules, in this order:

| # | Module | Responsibility |
|---|---|---|
| - | `Logger` | timestamped console logging |
| 1 | `SchemaData` | all enumerations, patterns and the column definitions per sheet |
| 2 | `I18n` | EN/DE texts |
| 3 | `ConfigManager` | SRN / party ID / token handling and persistence |
| 4 | `TemplateGenerator` | serves the embedded Excel template |
| 5 | `ExcelParser` | reads the workbook, maps columns, structural pre-flight |
| 6 | `ValidationEngine` | schema-level and cross-field checks, finding catalogue |
| 7 | `XMLGenerator` | builds the XML (plain string concatenation, fixed element order) and the **self-check** |
| 8 | `ZipPackager` | splits devices into `DEVICE.POST` / `UDI_DI.POST` sets, batches, ZIP, records |
| 9 | `UI` | wizard, worklist, event handling |

Find them with `grep -n "^// MODULE" eudamed-xml-generator.html`.

> **Editing tips.** A few lines of the file are several hundred kilobytes long (minified CSS, the inlined
> libraries, the base64 template). Never print the file blindly; use `grep -n ... | cut -c1-160` or an editor
> that handles long lines. The XML is built by string concatenation with a hard-coded element order, so a
> change in element sequence means reordering the concatenation in `buildBasicUDI` / `buildUDIDIContent`.

## Running the tests

```bash
pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

| Test module | What it protects |
|---|---|
| `test_app_static.py` | every script block parses (a syntax error silently kills the whole page); version numbers are consistent; the app code contains no network API and the markup loads no external resource; the embedded template's headers match the columns the code expects and carry no personal metadata |
| `test_check_xml.py` | one positive and one negative case for every documented portal rule, plus the examples |
| `test_repo_hygiene.py` | no data files, no acknowledgements, no e-mail addresses or absolute user paths, license files in place |

**XSD tests.** The EUDAMED schemas are not bundled. To also validate against them, download the schema package
and point the tests at it (the directory must contain `service/Message.xsd`):

```bash
EUDAMED_XSD_DIR=/path/to/dtx-schemas python -m unittest discover -s tests -v     # Linux / macOS
set EUDAMED_XSD_DIR=C:\path\to\dtx-schemas && python -m unittest discover -s tests -v   # Windows
```

> **A syntax check is not optional.** After *every* edit of the HTML run `test_app_static.py`. A single
> stray line break inside a JavaScript string or regex literal makes the browser skip the entire script block:
> the page loads but every button is dead, with the error visible only in the browser console. Counting
> brackets does **not** catch this - parsing does.

### Roadmap: executing the JavaScript

The tests parse the application JavaScript but do not execute it. The most valuable next contribution is a
headless test (for example Node + jsdom, or a browser driver) that loads the page, feeds it a small synthetic
workbook, and compares the generated XML with `examples/messages`. Pull requests welcome.

## The self-check - where portal knowledge lives

`XMLGenerator.selfCheck()` runs on every generated message before it is added to the ZIP and **aborts the
download** if a rule is violated. It exists because several portal rules are invisible to XSD validation
(see [`eudamed-portal-rules.md`](eudamed-portal-rules.md)). When you learn a new rule from a real
acknowledgement, add it in all of these places:

1. `XMLGenerator.selfCheck()` (marked *observed* or *derived* in the comment),
2. `tools/check_xml.py`,
3. a positive and a negative test in `tests/test_check_xml.py`,
4. `docs/eudamed-portal-rules.md` (with its evidence level) and the changelog.

## Bumping the EUDAMED schema version

1. In the new schema package, read the `fixed` value of the `version` attribute in `service/Message/MessageType.xsd`.
2. Update `SCHEMA_VERSION` **and** the separate `REQUIRED_VERSION` literal in `selfCheck()` (they are
   separate on purpose so a half-done bump fails loudly; a test checks they agree), `REQUIRED_VERSION` in
   `tools/check_xml.py`, the `version-tag`/footer text, and the text in the template's `INSTRUCTIONS` sheet.
3. Re-validate the examples against the new schemas, review enumerations and patterns in `SchemaData`
   against the changed XSD files, and add a changelog entry.

## Editing the embedded Excel template

`TEMPLATE_B64` is a complete `.xlsx` file, base64-encoded on a single line. To change it: decode it, modify
the workbook **in place** (do not rebuild it from scratch - that loses formats, drop-downs, comments and freeze
panes), re-encode, and replace the string. Keep identifier columns formatted as text, keep placeholder
identifiers obviously fake, and re-run the tests (they compare the template headers with the code).
Never put real device data, SRNs, certificate numbers or personal names in the template.

## Versioning and releases

* SemVer for the application: breaking changes of the workbook format or generated output -> major;
  new features -> minor; fixes -> patch.
* To release: update `VERSION`, `APP_VERSION`, the `version-tag` and footer text, and move the
  `[Unreleased]` entries in `CHANGELOG.md` under the new version heading; run the tests; commit; tag
  `vX.Y.Z`; push the tag. The release workflow checks that the tag equals `VERSION`, re-runs the tests and
  attaches the HTML file (named with the version) and a SHA-256 sum to a GitHub release.
