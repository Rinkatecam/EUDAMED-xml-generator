# EUDAMED DTX: rules the schema does not tell you

A message can be perfectly valid against the XSD and still be rejected by the EUDAMED portal. This page
collects what the generator's authors learned the hard way, so you do not have to.

**Evidence levels** used below:

| Tag | Meaning |
|---|---|
| **XSD** | Follows directly from the schema files; you can verify it yourself. |
| **Observed** | Seen in real portal acknowledgements (August-September 2026). Not derivable from the XSD. EUDAMED changes - re-verify before relying on it and please report differences. |
| **Release notes** | Stated in the European Commission's EUDAMED release notes. |

Everything here concerns MDR devices submitted through the DTX data exchange.

---

## 1. The message version is pinned (XSD, Release notes)

`MessageType.xsd` declares the `version` attribute of the message as
`use="required" fixed="3.0.30"`. Any other value makes the whole message invalid against the schema. After
every schema drop, check this attribute first.

The release notes list a known issue where Bulk Upload does **not** reject a request that declares the wrong
XSD version for the environment (ticket `EUDAMEDMDR-45539`). Do not rely on the portal to catch a version
mismatch: validate locally.

## 2. The portal selection must match the file's service (Observed)

The upload mechanism you choose in the portal is compared, as plain text, with the `serviceID` and
`serviceOperation` inside your file. A mismatch is rejected before any content is read:

```
responseCode       BAD_REQUEST
operationErrorCode E-I-40000
operationDetail    ERR-DTX-EUD-103.03-02: Provided XML service DEVICE.POST does not match selected UDI_DI.POST service.
```

`E-I-40000` is a generic code - it is not specific to this error (it is also used for throttling). Always read
`operationDetail` and the `ERR-DTX-...` code.

The portal's mechanisms correspond one-to-one to the service combinations of the official sample messages:

| Portal mechanism | Service | Payload root element |
|---|---|---|
| Upload of Legacy / Regulation Device / SPP (Basic UDI **and** UDI-DI / Master UDI-DI) | `DEVICE.POST` | `device:Device` (Basic UDI + UDI-DI) |
| Upload of UDI-DI / Master UDI-DI for **existing** Basic UDI-DI | `UDI_DI.POST` | `device:UDIDIData` |
| Update Basic UDI | `BASIC_UDI.PATCH` | `device:BasicUDI` |
| Update UDI-DI / Master UDI-DI | `UDI_DI.PATCH` | `device:UDIDIData` |
| Update market information | `MARKET_INFO.PUT` | `mktinfo:DTXMarketInfo` |
| Update container package | `PACKAGE_UDI.PUT` | `device:DTXPackageUDI` |
| Update product original manufacturer | `PRODUCT_DESIGNER.PUT` | `pd:DTXProductDesigner` |
| Download of legacy/regulation device/SPP | `DEVICE.GET` | pull request with criteria |
| Actor download | `ACTOR.GET` | pull request with criteria |
| SSCP download | `SSCP.GET` | pull request with criteria |

The service blocks echoed in an acknowledgement come from **your file**, not from the portal selection, so
the acknowledgement cannot tell you which option you picked.

## 3. One entity type per message, at most 300 (XSD)

In `CoreEntityPayloadType` the payload is an `xs:choice` with `maxOccurs="1"` on the choice itself: a
message contains **either** `device:Device` **or** `device:UDIDIData` (never both), repeated up to 300 times.
A message that mixes them is schema-invalid. This is why creating a Basic UDI and adding UDI-DIs to it need
two separate files.

## 4. A Basic UDI-DI can be created only once (Observed)

Every `device:Device` carries its own copy of the Basic UDI. If several `device:Device` entries in the same
or in earlier messages declare the same Basic UDI-DI, EUDAMED accepts one and rejects every other as a
duplicate:

```
operationErrorCode    basicUdiDatas[0].basicUdi
operationErrorDetail  The device identifier code <BASIC-UDI-DI> already exists for the selected issuing agency <AGENCY>
responseCode          PROCESSED_WITH_ERRORS
```

Details worth knowing:

* The whole entity is rejected - the UDI-DI inside it is **not** registered either.
* `entityCode` in each error block is the **Basic UDI-DI**, not the UDI-DI.
* The accepted entity is **not necessarily the first one in the file** (it was seen mid-batch), so
  "send them in order" does not help.
* The message is XSD-valid, so no schema check can catch it.

**Consequence:** send exactly **one** `device:Device` per new Basic UDI-DI (`DEVICE.POST`), and add all other
UDI-DIs with `device:UDIDIData` (`UDI_DI.POST`), which references the Basic UDI-DI via
`udidi:basicUDIIdentifier` instead of declaring it. Upload the creating messages first. If a family was
(partly) created earlier and you do not know which UDI-DI was accepted, send the whole family as
`UDI_DI.POST`; an already registered UDI-DI is then expected to be rejected on its own.
This is what the generator does. `device:UDIDIData` uses `xsi:type="udidi:MDRUDIDIDataType"` (the schema
itself marks the `device:`-namespace wrapper type as "do not use").

> Status (as of November 2026): `UDI_DI.POST` messages of this shape - UDI-DIs added to an existing Basic
> UDI-DI - are **confirmed to be accepted by the live portal** (evidence level: Observed). Behaviour for an
> already-registered UDI-DI, and the `entityCode` echoed in `UDI_DI.POST` acknowledgements, have not been
> documented here yet - contributions with anonymised acknowledgements are very welcome.

## 5. Language of comment texts (Observed)

`commondi:comments` (inside storage conditions and critical warnings) is a
`LanguageOptionalTextsType`: the XSD makes `<lsn:language>` optional, and the official sample messages omit
it. The portal is stricter, in two steps:

1. **A language is mandatory.** A comment without `<lsn:language>` is rejected:
   `ERR-DTX-UDI-094.05-01 Language is required for the current attribute`.
2. **For coded conditions the language must be `ANY`.** Writing a real language (e.g. `EN`) next to a coded
   storage condition is rejected:
   `ERR-DTX-UDI-028.05-03 Language other than 'ANY' is not a valid value for storage type other than 'SHC099'`.

The split follows the schema's own footnotes: the temperature codes (`SHC006`, `SHC007`, `SHC008`) are coded
values whose comment is only supplementary (**`ANY`**), while the free-text codes (`SHC099`, `CW999`) carry
real text (**a real language**). The element order inside the comment is `language` first, then `textValue`.
The mirrored rule for critical warnings other than `CW999` is derived, not observed.

## 6. Scalar constraints that are easy to get wrong (XSD)

| Element | Constraint |
|---|---|
| `DICode`, `certificateNumber`, `certificateRevisionNumber` | 1-120 characters (not 255) |
| `model`, `modelName/name`, `referenceNumber`, `website` | 1-255 characters |
| `lsn:textValue` | 1-2000 characters |
| `CASCode` | pattern `\d{1,7}-\d{2}-\d`, max. 12 characters |
| `ECCode` | pattern `\d{3}-\d{3}-\d`, exactly 9 characters |
| `NBActorCode` | exactly 4 digits (keep the leading zero - format the Excel column as text) |
| SRN | `<country>-<AR\|MF\|SP\|IM\|PR>-<9 digits>` with a fixed country list, or `NA` |
| `numberOfReuses` | integer between -1 and 32767 (`xs:short`) |
| Dates | `xs:date`, `YYYY-MM-DD` |

## 7. `numberOfReuses` (XSD)

The schema documents `-1` (no defined maximum), `0` (single-use device) and a positive number (the reuse
limit); the type's minimum is `-1`, and the official samples use `-1`. The value is mandatory. The generator
deliberately **never fills it in for you**: it is a regulatory statement about the device, so a blank cell
blocks generation.

## 8. Excel pitfalls (Observed)

* **HIBCC codes start with `+` or `++`.** In a cell that is not formatted as text, Excel turns such a code
  into a formula and shows `#NAME?`. The template formats the code columns as text; keep it that way when
  you paste data in.
* **Drag-fill increments identifiers.** Dragging a cell down can silently turn one SRN into a sequence
  (`...196`, `...197`, ...). All rows of one Basic UDI-DI family must carry identical Basic UDI data; the
  validator reports inconsistencies.
* Leading/trailing spaces in codes are trimmed by the generator.

## 9. Throttling (Release notes)

The release notes announce a throttling mechanism for the DTX services: when unusual traffic is detected
within 24 hours, messages of an individual user are rejected. Spread large submissions over time and do not
fire all files at once.

## 10. The general lesson

"The XSD allows it" and "the official sample does it" are **not** sufficient evidence that the portal accepts
something. Only a real acknowledgement is authoritative. Whenever you learn a new portal rule, add it to the
generator's self-check, to `tools/check_xml.py`, to a test, and to this page.

## Sources

* EUDAMED release notes: <https://webgate.ec.europa.eu/eudamed-help/en/files/EUDAMED%20-%20release%20notes.pdf>
* EUDAMED data exchange (machine-to-machine) documentation:
  <https://webgate.ec.europa.eu/eudamed-help/en/data-exchange/machine-to-machine/message-exchange.html>
* The XSD schemas and sample messages published by the European Commission.
