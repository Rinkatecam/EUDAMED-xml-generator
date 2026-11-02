"""Static checks of the single-file application: syntax, versioning, network silence, template."""
import io
import re
import unittest

import helpers as h

try:
    import esprima
except ImportError:  # pragma: no cover
    esprima = None

try:
    import openpyxl
except ImportError:  # pragma: no cover
    openpyxl = None


@unittest.skipIf(esprima is None, "pip install esprima")
class TestSyntax(unittest.TestCase):
    def test_every_script_block_parses(self):
        blocks = h.script_blocks()
        self.assertGreaterEqual(len(blocks), 3, "expected the vendor blocks plus the application block")
        for i, block in enumerate(blocks, 1):
            with self.subTest(block=i):
                try:
                    esprima.parseScript(block)
                except Exception as exc:  # esprima raises its own error types
                    self.fail(f"script block {i} does not parse: {exc}")


class TestVersioning(unittest.TestCase):
    def setUp(self):
        self.version = h.read_text("VERSION").strip()

    def test_version_file_is_semver(self):
        self.assertRegex(self.version, r"^\d+\.\d+\.\d+$")

    def test_app_version_matches_version_file(self):
        self.assertEqual(h.js_const_string("APP_VERSION"), self.version)

    def test_visible_version_labels_match(self):
        html = h.app_html()
        self.assertIn(f'<span class="version-tag">v{self.version} &middot;', html)
        self.assertIn(f"EUDAMED XML Generator v{self.version} &mdash;", html)
        self.assertIn(f"Version {self.version} |", html)  # header comment

    def test_changelog_top_release_matches(self):
        releases = re.findall(r"^## \[(\d+\.\d+\.\d+)\]", h.read_text("CHANGELOG.md"), re.M)
        self.assertTrue(releases, "CHANGELOG.md has no release heading")
        self.assertEqual(releases[0], self.version)

    def test_schema_version_is_single_sourced(self):
        schema = h.js_const_string("SCHEMA_VERSION")
        # the self-check keeps its own literal on purpose; it must agree with the constant
        m = re.search(r"const REQUIRED_VERSION = '([\d.]+)';", h.app_html())
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), schema)
        # both message builders take the version from the constant, no stray literals
        self.assertEqual(h.app_html().count("""' version="' + SCHEMA_VERSION + '">"""), 2)
        self.assertNotIn(f'version="{schema}"', h.app_code())
        self.assertIn(schema, h.read_text("README.md"))


class TestNoNetwork(unittest.TestCase):
    """The README promises that nothing is loaded from or sent to the network."""

    def test_no_external_resources_in_markup(self):
        html = h.app_html()
        # <script src=...>, <link href=http...>, <img src=http...>, iframes, CSS imports / remote url()
        self.assertNotRegex(html, r"<script[^>]+\bsrc\s*=")
        self.assertNotRegex(html, r"<link[^>]+href\s*=\s*[\"']https?://")
        self.assertNotRegex(html, r"<(img|iframe|embed|object|video|audio|source)[^>]+(src|data)\s*=\s*[\"']?https?://")
        self.assertNotRegex(html, r"@import")
        self.assertNotRegex(html, r"url\(\s*[\"']?https?://")

    def test_application_code_uses_no_network_apis(self):
        code = h.app_code()
        for api in ("fetch(", "XMLHttpRequest", "WebSocket", "sendBeacon", "EventSource", "importScripts"):
            with self.subTest(api=api):
                self.assertNotIn(api, code)


@unittest.skipIf(openpyxl is None, "pip install openpyxl")
class TestEmbeddedTemplate(unittest.TestCase):
    SHEETS = {
        "DEVICES": "DEVICE_COLUMNS",
        "MARKET_INFO": "MARKET_COLUMNS",
        "SUBSTANCES": "SUBSTANCE_COLUMNS",
        "STORAGE AND HANDLING": "STORAGE_COLUMNS",
    }

    @classmethod
    def setUpClass(cls):
        cls.wb = openpyxl.load_workbook(io.BytesIO(h.template_bytes()))

    def test_sheet_names(self):
        self.assertEqual(self.wb.sheetnames, [*self.SHEETS, "LEGEND", "INSTRUCTIONS"])

    def test_headers_match_the_columns_the_code_expects(self):
        for sheet, const in self.SHEETS.items():
            with self.subTest(sheet=sheet):
                actual = [c.value for c in self.wb[sheet][1] if c.value is not None]
                self.assertEqual(actual, h.js_column_headers(const))

    def test_every_header_has_a_comment(self):
        for sheet in self.SHEETS:
            with self.subTest(sheet=sheet):
                missing = [c.value for c in self.wb[sheet][1] if c.value and not c.comment]
                self.assertEqual(missing, [])

    def test_no_personal_metadata(self):
        z = h.template_zip()
        core = z.read("docProps/core.xml").decode("utf-8")
        self.assertNotIn("@", core)
        self.assertIn("<dc:creator", core)
        self.assertRegex(core, r">openpyxl<")
        for name in z.namelist():
            if name.startswith("xl/comments/"):
                authors = set(re.findall(r"<author>(.*?)</author>", z.read(name).decode("utf-8")))
                self.assertTrue(authors <= {"EUDAMED Generator", "EUDAMED XML Generator"}, (name, authors))

    def test_example_row_uses_only_placeholder_identifiers(self):
        row = {self.wb["DEVICES"].cell(row=1, column=c).value: self.wb["DEVICES"].cell(row=2, column=c).value
               for c in range(1, self.wb["DEVICES"].max_column + 1)}
        self.assertEqual(row["BUDI_MFActorCode"], "DE-MF-000000000")
        self.assertEqual(row["CERT_NBActorCode"], "0000")
        self.assertTrue(str(row["BUDI_DICode"]).startswith("++EXAMPLE"))
        self.assertTrue(str(row["UDI_DICode"]).startswith("+EXAMPLE"))

    def test_substance_example_is_a_neutral_placeholder(self):
        ws = self.wb["SUBSTANCES"]
        row = {ws.cell(row=1, column=c).value: ws.cell(row=2, column=c).value for c in range(1, ws.max_column + 1)}
        self.assertTrue(str(row["UDI_DICode"]).startswith("+EXAMPLE"))
        self.assertEqual(row["SUB_Name_EN"], "Example substance")
        self.assertEqual((row["SUB_CASCode"], row["SUB_ECCode"]), ("0000-00-0", "000-000-0"))

    def test_instructions_name_the_targeted_schema(self):
        text = h.template_zip().read("xl/worksheets/sheet6.xml").decode("utf-8")
        self.assertIn("v" + h.js_const_string("SCHEMA_VERSION"), text)
        self.assertNotIn("3.0.25", text)


if __name__ == "__main__":
    unittest.main()
