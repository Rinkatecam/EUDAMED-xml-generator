"""Shared helpers for the test-suite (standard library only, except where noted)."""
from __future__ import annotations

import base64
import io
import os
import re
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_PATH = os.path.join(ROOT, "eudamed-xml-generator.html")

# make ``tools`` and ``tests`` importable no matter where the runner was started from
for _p in (os.path.join(ROOT, "tools"), os.path.join(ROOT, "tests")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

_cache: dict[str, str] = {}


def read_text(rel: str) -> str:
    path = os.path.join(ROOT, rel)
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def app_html() -> str:
    if "app" not in _cache:
        _cache["app"] = read_text("eudamed-xml-generator.html")
    return _cache["app"]


def script_blocks() -> list[str]:
    return re.findall(r"<script>(.*?)</script>", app_html(), re.S)


def js_const_string(name: str) -> str:
    """Value of ``const NAME = '...';`` in the application script."""
    m = re.search(r"const %s = '([^']*)';" % re.escape(name), app_html())
    if not m:
        raise AssertionError(f"const {name} not found in the application")
    return m.group(1)


def app_code() -> str:
    """The application's own code: everything from the metadata constants on (excludes the
    minified third-party blobs that precede it)."""
    html = app_html()
    return html[html.index("const APP_NAME"):]


def template_bytes() -> bytes:
    m = re.search(r"const TEMPLATE_B64 = '([A-Za-z0-9+/=]+)'", app_html())
    if not m:
        raise AssertionError("TEMPLATE_B64 not found")
    return base64.b64decode(m.group(1))


def template_zip() -> zipfile.ZipFile:
    return zipfile.ZipFile(io.BytesIO(template_bytes()))


def js_column_headers(const_name: str) -> list[str]:
    """Headers declared in ``const <const_name> = [ { key:'..', header:'..', ... }, ... ];``."""
    m = re.search(r"const %s = \[\n(.*?)\n    \];" % re.escape(const_name), app_html(), re.S)
    if not m:
        raise AssertionError(f"{const_name} not found")
    return re.findall(r"header:'([^']*)'", m.group(1))


def repo_files(skip_dirs=(".git", "__pycache__", ".pytest_cache")):
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            yield os.path.relpath(full, ROOT).replace(os.sep, "/"), full
