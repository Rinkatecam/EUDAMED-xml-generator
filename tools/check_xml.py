#!/usr/bin/env python3
"""Independent checker for EUDAMED DTX ``Push`` messages (MDR devices).

Works on files from *any* source, not only from this generator. It checks the rules that are
documented in ``docs/eudamed-portal-rules.md`` - the ones a plain XSD validation does NOT catch -
and, if you point it at a local copy of the EUDAMED schemas, also validates against the XSD.

    python tools/check_xml.py message.xml [more.xml ...]
    python tools/check_xml.py --xsd-dir /path/to/dtx-schemas message.xml

``--xsd-dir`` must contain ``service/Message.xsd`` (the layout the European Commission publishes).
The portal-rule checks use only the Python standard library; XSD validation needs ``lxml``.

Exit status: 0 = no errors (warnings are allowed), 1 = at least one error, 2 = usage problem.

This is a Python re-implementation of the self-check built into the generator, plus a few extra
rules that only make sense for finished files (for example duplicate Basic UDI declarations).
"""
from __future__ import annotations

import argparse
import os
import sys
import xml.etree.ElementTree as ET
from collections import Counter

REQUIRED_VERSION = "3.0.30"      # MessageType.xsd pins it as a fixed attribute
MAX_ENTITIES = 300               # CoreEntityPayloadType: maxOccurs="300" per entity type
LSN_NS = "https://ec.europa.eu/tools/eudamed/dtx/datamodel/Entity/Common/LanguageSpecific/v1"
PLACEHOLDER_TOKEN = "<!-- TOKEN -->"

# payload root element -> (serviceID, serviceOperation) the message has to be sent with
SERVICE_FOR_PAYLOAD = {
    "Device": ("DEVICE", "POST"),
    "UDIDIData": ("UDI_DI", "POST"),
}

ERROR, WARNING = "error", "warning"


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def _ns(tag: str) -> str:
    return tag[1:].split("}", 1)[0] if tag.startswith("{") else ""


def _child(el, name):
    for c in el:
        if _local(c.tag) == name:
            return c
    return None


def _desc_text(el, name):
    """Text of the first descendant with the given local name, or None."""
    for x in el.iter():
        if _local(x.tag) == name:
            return (x.text or "").strip()
    return None


def check_message(data: bytes | str, label: str = "") -> list[tuple[str, str]]:
    """Return a list of (severity, message) findings for one Push message."""
    out: list[tuple[str, str]] = []

    def err(msg):
        out.append((ERROR, msg))

    def warn(msg):
        out.append((WARNING, msg))

    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        return [(ERROR, f"not well-formed XML: {exc}")]

    if _local(root.tag) != "Push":
        err(f"root element is <{_local(root.tag)}>, expected a Push message")
        return out

    # (1) version pin ------------------------------------------------------------------------
    version = root.get("version")
    if version != REQUIRED_VERSION:
        err(f'version="{version}" instead of "{REQUIRED_VERSION}" (MessageType.xsd pins it)')

    # (2) payload shape -----------------------------------------------------------------------
    payload = _child(root, "payload")
    entities = [c for c in payload] if payload is not None else []
    kinds = Counter(_local(e.tag) for e in entities)
    if payload is None or not entities:
        err("the payload is empty")
    if len(kinds) > 1:
        err("payload mixes " + " and ".join(sorted(kinds)) +
            " - the schema allows only one entity type per message")
    if len(entities) > MAX_ENTITIES:
        err(f"{len(entities)} entities in one message (maximum {MAX_ENTITIES})")

    # (3) service/payload agreement, in the recipient AND the sender block --------------------
    expected = None
    if len(kinds) == 1:
        kind = next(iter(kinds))
        expected = SERVICE_FOR_PAYLOAD.get(kind)
        if expected is None:
            warn(f"payload element <{kind}> is not covered by this checker; only generic checks were applied")
    for role in ("recipient", "sender"):
        block = _child(root, role)
        service = _child(block, "service") if block is not None else None
        if service is None:
            err(f"<{role}> has no <service> block")
            continue
        sid = _desc_text(service, "serviceID")
        sop = _desc_text(service, "serviceOperation")
        if expected and (sid, sop) != expected:
            err(f"<{role}> service is {sid}.{sop} but the payload requires {expected[0]}.{expected[1]}")
        if role == "recipient":
            token = _desc_text(service, "serviceAccessToken")
            if token is None or token == "" or token == PLACEHOLDER_TOKEN:
                warn("the access token is missing or still the placeholder - insert yours before uploading")

    # (4) a Basic UDI-DI may be declared by only one device:Device (business rule) ------------
    declared = Counter()
    for dev in entities:
        if _local(dev.tag) != "Device":
            continue
        basic = next((c for c in dev if _local(c.tag).endswith("BasicUDI")), None)
        ident = _child(basic, "identifier") if basic is not None else None
        if ident is not None:
            declared[(_desc_text(ident, "DICode"), _desc_text(ident, "issuingEntityCode"))] += 1
    for (code, agency), n in declared.items():
        if n > 1:
            err(f"Basic UDI-DI {code} ({agency}) is declared by {n} device:Device entries in this message - "
                "EUDAMED lets a Basic UDI-DI be created only once; send the other UDI-DIs as UDI_DI.POST")

    # (5) language rules for texts ---------------------------------------------------------------
    missing = sum(
        1 for e in root.iter()
        if _local(e.tag) == "name" and _ns(e.tag) == LSN_NS and _child(e, "language") is None
    )
    if missing:
        err(f"{missing} <lsn:name> block(s) without <lsn:language> (ERR-DTX-UDI-094.05-01)")

    bad_storage = 0
    for cond in (e for e in root.iter() if _local(e.tag) == "condition"):
        code = _desc_text(cond, "storageHandlingConditionValue")
        lang = _desc_text(cond, "language")
        if not code or lang is None:
            continue
        if (code != "SHC099" and lang != "ANY") or (code == "SHC099" and lang == "ANY"):
            bad_storage += 1
    if bad_storage:
        err(f"{bad_storage} storage condition(s) with the wrong comment language "
            "(ERR-DTX-UDI-028.05-03: coded values need ANY, SHC099 needs a real language)")

    bad_warning = 0
    for w in (e for e in root.iter() if _local(e.tag) == "warning"):
        code = _desc_text(w, "warningValue")
        lang = _desc_text(w, "language")
        if not code or lang is None:
            continue
        if (code == "CW999" and lang == "ANY") or (code != "CW999" and lang != "ANY"):
            bad_warning += 1
    if bad_warning:
        err(f"{bad_warning} critical warning(s) with the wrong comment language "
            "(CW999 needs a real language, coded warnings ANY - derived rule, not yet observed on the portal)")

    return out


def validate_xsd(path: str, xsd_dir: str) -> list[tuple[str, str]]:
    """Validate one file against <xsd_dir>/service/Message.xsd. Requires lxml."""
    try:
        from lxml import etree
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("XSD validation needs lxml (pip install lxml)") from exc
    entry = os.path.join(xsd_dir, "service", "Message.xsd")
    if not os.path.isfile(entry):
        raise FileNotFoundError(f"{entry} not found - --xsd-dir must contain service/Message.xsd")
    parser = etree.XMLParser(no_network=True, resolve_entities=False)
    schema = etree.XMLSchema(etree.parse(entry, parser))
    try:
        doc = etree.parse(path, parser)
    except etree.XMLSyntaxError as exc:
        return [(ERROR, f"not well-formed XML: {exc}")]
    if schema.validate(doc):
        return []
    return [(ERROR, f"XSD line {e.line}: {e.message}") for e in schema.error_log]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Check EUDAMED DTX Push messages against documented portal rules.")
    ap.add_argument("files", nargs="+", help="XML message files")
    ap.add_argument("--xsd-dir", help="directory that contains service/Message.xsd (optional XSD validation)")
    args = ap.parse_args(argv)

    failed = False
    for path in args.files:
        try:
            with open(path, "rb") as fh:
                data = fh.read()
        except OSError as exc:
            print(f"[ERROR] {path}: {exc}")
            failed = True
            continue
        findings = check_message(data, path)
        if args.xsd_dir:
            try:
                findings += validate_xsd(path, args.xsd_dir)
            except (RuntimeError, FileNotFoundError) as exc:
                print(f"[USAGE] {exc}")
                return 2
        errors = [m for s, m in findings if s == ERROR]
        warnings = [m for s, m in findings if s == WARNING]
        status = "FAIL" if errors else ("OK (with warnings)" if warnings else "OK")
        print(f"[{status}] {path}")
        for m in errors:
            print(f"    error:   {m}")
        for m in warnings:
            print(f"    warning: {m}")
        failed = failed or bool(errors)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
