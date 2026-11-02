# Workbook format

The generator reads one Excel workbook with these sheets. Download the formatted template from step 2 of
the application - **the template is the authoritative column reference**: every header has a bilingual
(EN/DE) cell comment, the fixed-value columns have drop-down lists, and the `LEGEND` sheet maps every column
to the XML element it ends up in. This page deliberately does not repeat that list, so the two can never
drift apart (a test checks that the template headers match the columns the code expects).

| Sheet | Granularity | Purpose |
|---|---|---|
| `DEVICES` | one row per **UDI-DI** | Basic UDI-DI data (`BUDI_*`), UDI-DI data (`UDI_*`), the device certificate link (`CERT_*`) and a few optional 3.0.30 fields. |
| `MARKET_INFO` | one row per UDI-DI | Countries where the device is made available / was originally placed on the market. |
| `SUBSTANCES` | one row per device-substance pair | Only for devices containing CMR / endocrine-disrupting / medicinal-product substances. |
| `STORAGE AND HANDLING` | one row per UDI-DI | Storage temperature limits, warning and contraindication text. |
| `LEGEND`, `INSTRUCTIONS` | - | Column reference and usage notes (bilingual). Ignored on import. |

## How the sheets belong together

* The sheets are joined by **`UDI_DICode` + `UDI_IssuingEntity`**, not by row position. Rows in
  `MARKET_INFO`, `SUBSTANCES` and `STORAGE AND HANDLING` that match no row in `DEVICES` are reported.
* A **Basic UDI-DI family** is all `DEVICES` rows that share the same `BUDI_DICode`. All Basic-UDI columns
  (`BUDI_*`, including the manufacturer SRN and the certificate) must be identical across the family; the
  validator reports rows that deviate. Each UDI-DI may appear only once.
* How a family ends up in the output (one `DEVICE.POST` row, the rest as `UDI_DI.POST`) is described in the
  [README](../README.md#how-to-upload-the-important-part).

## Formatting rules

* Booleans are `TRUE` / `FALSE`; dates are `YYYY-MM-DD`.
* Keep identifier columns formatted as **text**. HIBCC codes begin with `+` / `++` and Excel otherwise turns
  them into formulas (`#NAME?`); Notified Body numbers need their leading zeros.
* `MKT_Country` may hold several countries separated by commas (`AT,BE,DE`). `MKT_OriginalPlaced` is
  `TRUE`/`FALSE` for all listed countries, or a country list (e.g. `DE`): `TRUE` for those, `FALSE` for the
  rest of the row's countries.
* `UDI_MDNCodes` and `UDI_ProductionIdentifier` accept several values separated by spaces.
* `UDI_NumberOfReuses` is mandatory and never defaulted: `-1` (no defined maximum), `0` (single-use) or the
  reuse limit. See [`eudamed-portal-rules.md`](eudamed-portal-rules.md#7-numberofreuses-xsd).
* In `STORAGE AND HANDLING`, `FALSE` or an empty cell means "none" for warning and contraindication.
* Unknown extra columns are ignored and missing *optional* columns are treated as empty, so workbooks
  created with an older template keep working. Missing required columns and sheets are caught up front
  ("structural pre-flight") with a message naming exactly what is missing.
