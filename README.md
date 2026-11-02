# EUDAMED XML Generator

Turn an Excel workbook of device data into **EUDAMED DTX XML messages** (MDR devices) - in your
browser, offline, with nothing to install.

> **Unofficial community project.** Not affiliated with, endorsed by, or supported by the European
> Commission. EUDAMED, its schemas and its portal belong to their respective owners. See
> [Disclaimer](#disclaimer).

* **One file.** Download `eudamed-xml-generator.html`, open it in a current browser, done.
* **Private by design.** Everything runs locally. No data is uploaded and no external resources are
  loaded (a test enforces this). Your SRN, device data and access token never leave your machine.
* **Targets EUDAMED DTX XSD schema `3.0.30`** (see [Versioning](#versioning)).
* **Bilingual** interface and Excel template (English / Deutsch).
* **Encodes hard-won portal knowledge** that the XSD does not tell you - see
  [`docs/eudamed-portal-rules.md`](docs/eudamed-portal-rules.md).

## Quick start

1. Download the HTML file from the [latest release](../../releases/latest) and open it in your browser.
2. **Step 1 - Config:** enter your SRN and party ID (the access token is optional; a placeholder is
   written if you leave it empty).
3. **Step 2 - Template:** download the Excel template and fill it - one row per UDI-DI. Every column has
   a drop-down and a cell comment; the `LEGEND` and `INSTRUCTIONS` sheets explain the rest
   (see also [`docs/workbook-format.md`](docs/workbook-format.md)).
4. **Step 3 - Upload** your workbook, **Step 4 - Validate** (the worklist shows the exact cells to fix),
   **Step 5 - Generate** the ZIP.
5. Upload the files in the EUDAMED portal - **in the order described below**.

## How to upload (the important part)

EUDAMED lets a Basic UDI-DI be **created only once**. A message that declares an existing Basic UDI-DI
again is rejected - even though it is perfectly valid against the XSD. The generator therefore writes
two sets of files into the ZIP:

| Folder | Contains | Portal upload mechanism | Service |
|---|---|---|---|
| `1_DEVICE_POST/` | exactly **one** UDI-DI per new Basic UDI-DI family (creates the family) | *Upload of Legacy / Regulation Device / SPP (Basic UDI and UDI-DI / Master UDI-DI)* | `DEVICE.POST` |
| `2_UDI_DI_POST/` | **all other** UDI-DIs (added to the now-existing family) | *Upload of UDI-DI / Master UDI-DI for existing Basic UDI-DI* | `UDI_DI.POST` |

1. Upload folder **1** first and wait until the Basic UDI-DIs are accepted.
2. Then upload folder **2**.
3. If some Basic UDI-DIs already exist in EUDAMED from an earlier upload, paste them into
   **"Basic UDIs already in EUDAMED"** before generating - their whole family is then generated as
   `UDI_DI.POST` only.
4. The mechanism you select in the portal **must match** the service inside the file, otherwise EUDAMED
   answers with `ERR-DTX-EUD-103.03-02`. `UPLOAD_INSTRUCTIONS.txt` in the ZIP repeats all of this for
   your concrete files. Pace your uploads: EUDAMED applies throttling to DTX services.

## What the generator checks - and what it cannot

Checked locally: schema constraints (patterns, lengths, enumerations, ranges), cross-field rules,
consistency inside one Basic UDI-DI family, and a set of portal rules the XSD cannot express (see the
self-check described in [`docs/development.md`](docs/development.md)).

**Not checkable offline:** whether an SRN is registered, whether a certificate is valid, whether an EMDN
code exists, duplicates against what is already in EUDAMED, and the portal's own business rules. A file
that passes every local check can still be rejected - always inspect the acknowledgement.

## Output

The ZIP contains the XML message files (max. 300 entities each), `UPLOAD_INSTRUCTIONS.txt`, a
`SUBMISSION_RECORD.txt` / `submission_record.json` (input hash, settings with the token redacted, validation
summary, SHA-256 of every file) and optionally the validation report. **Generated files contain your SRN and,
if entered, your access token - treat them as confidential.**

## Privacy and security

* No network access from the application code; no analytics; no web fonts.
* Your SRN and party ID are remembered in your browser's `localStorage` between sessions. The access token
  is only remembered if you tick *Remember the security token* (off by default). **Clear saved credentials**
  removes everything; do not tick the box on shared machines.
* Please read [`SECURITY.md`](SECURITY.md) for how to report problems.

## Known limitations

* MDR devices only (no IVDR, no legacy MDD/AIMDD/IVDD devices).
* Services `DEVICE.POST` and `UDI_DI.POST` only (no actor, market-info, SSCP, certificate, ... services).
* Storage conditions are limited to temperature limits (`SHC006`/`SHC007`/`SHC008`); warnings are written as
  free text (`CW999`). Other codes, clinical sizes, packages, device marking, product designer and annex XVI
  fields are not generated.
* Automated tests cover syntax, version consistency, repository hygiene, template/schema consistency and
  the portal-rule checker. The application JavaScript is **not** yet executed by automated tests - see the
  roadmap in [`docs/development.md`](docs/development.md).
* The `UDI_DI.POST` message shape is validated against the XSD; reports from live portal runs are welcome.

## Examples and helper tools

* [`examples/messages/`](examples/messages) - small synthetic messages showing both shapes.
* [`tools/check_xml.py`](tools/check_xml.py) - independent checker for DTX messages from **any** source:
  portal rules always, XSD validation if you provide the schemas.

```bash
pip install -r requirements-dev.txt
python tools/check_xml.py examples/messages/*.xml
# with the EUDAMED schemas (not bundled, see below):
python tools/check_xml.py --xsd-dir /path/to/dtx-schemas examples/messages/*.xml
```

### Where do I get the XSD schemas?

They are published by the European Commission (the schema location used by EUDAMED's own sample messages is
`https://webgate.ec.europa.eu/tools/eudamed/dtx/service/Message.xsd`; imported files resolve relative to it).
See also the [EUDAMED data exchange documentation](https://webgate.ec.europa.eu/eudamed-help/en/data-exchange/machine-to-machine/message-exchange.html).
They are intentionally not redistributed in this repository.

## Versioning

* The tool follows [Semantic Versioning](https://semver.org/). Releases are git tags `vX.Y.Z`; the changes
  are listed in [`CHANGELOG.md`](CHANGELOG.md) and the version is stored in [`VERSION`](VERSION).
* The EUDAMED schema version the tool targets (`3.0.30`) is a separate number: EUDAMED pins it in
  `MessageType.xsd`, and messages declaring any other value are invalid. A new schema drop normally means a
  new release of this tool.

## Development

```bash
pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

See [`docs/development.md`](docs/development.md) and [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Disclaimer

This software is provided "as is", without warranty of any kind (see [`LICENSE`](LICENSE)). It is a
convenience tool; **you are solely responsible for the correctness and completeness of the data you submit
to EUDAMED** and for compliance with Regulation (EU) 2017/745. Always review generated files and the
portal's acknowledgements before relying on them. Do not publish real device data, SRNs, certificate numbers
or access tokens in issues or pull requests.

## License

[MIT](LICENSE). Bundled third-party components keep their own licenses - see
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

---

## Kurzfassung (Deutsch)

**EUDAMED XML Generator** wandelt eine Excel-Tabelle mit Produktdaten in EUDAMED-DTX-XML-Dateien (MDR) um -
komplett im Browser, offline, ohne Installation. Es werden keine Daten hochgeladen.

**Wichtig beim Hochladen:** EUDAMED legt eine Basic UDI-DI nur **einmal** an. Der Generator erzeugt deshalb
zwei Ordner: `1_DEVICE_POST/` (je neue Produktfamilie genau eine UDI-DI; Portal-Auswahl *"Upload of Legacy /
Regulation Device / SPP (Basic UDI and UDI-DI / Master UDI-DI)"*) und `2_UDI_DI_POST/` (alle weiteren UDI-DIs;
Portal-Auswahl *"Upload of UDI-DI / Master UDI-DI for existing Basic UDI-DI"*). Erst Ordner 1 hochladen und
abwarten, dann Ordner 2. Die im Portal gewählte Variante muss zum Dienst in der Datei passen. Bereits
angelegte Basic UDI-DIs trägt man vor dem Erzeugen im Feld *"Basic UDIs already in EUDAMED"* ein.

Inoffizielles Community-Projekt, nicht mit der Europäischen Kommission verbunden. Für Inhalt und
Richtigkeit der übermittelten Daten sind Sie selbst verantwortlich. Details: siehe oben und
[`docs/eudamed-portal-rules.md`](docs/eudamed-portal-rules.md).
