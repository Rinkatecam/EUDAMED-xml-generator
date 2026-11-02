"""Guards against accidentally publishing real data, credentials or personal information.

These checks are deliberately generic (they do not contain any real names or identifiers).
"""
import os
import re
import unittest

import helpers as h

TEXT_SUFFIXES = (".md", ".py", ".yml", ".yaml", ".txt", ".xml", ".html", ".json", ".cfg", ".toml", ".gitignore",
                 ".gitattributes", ".editorconfig")
TEXT_NAMES = {"LICENSE", "VERSION"}
FORBIDDEN_SUFFIXES = (".xlsx", ".xls", ".xlsm", ".zip", ".bak", ".pyc", ".env", ".pem", ".key", ".pfx")


def text_files():
    for rel, full in h.repo_files():
        if rel.endswith(TEXT_SUFFIXES) or os.path.basename(rel) in TEXT_NAMES or rel.startswith("third_party_licenses/"):
            yield rel, full


class TestRepositoryHygiene(unittest.TestCase):
    def test_no_data_or_secret_files(self):
        bad = [rel for rel, _ in h.repo_files() if rel.lower().endswith(FORBIDDEN_SUFFIXES)]
        self.assertEqual(bad, [], "data / binary / key files must not be committed")

    def test_no_acknowledgement_or_generated_output_files(self):
        bad = [rel for rel, _ in h.repo_files()
               if re.search(r"(^|/)(APP-DTX-\d+|EUDAMED_(DEVICE|UDI_DI)_POST_\d+)\.xml$", rel)
               or re.search(r"(^|/)EUDAMED_XML_\d{4}-\d{2}-\d{2}", rel)]
        self.assertEqual(bad, [])

    def test_no_large_files_besides_the_application(self):
        big = [(rel, os.path.getsize(full)) for rel, full in h.repo_files()
               if rel != "eudamed-xml-generator.html" and os.path.getsize(full) > 500_000]
        self.assertEqual(big, [])

    def test_no_email_addresses(self):
        pat = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z0-9.-]+")
        hits = []
        for rel, full in text_files():
            with open(full, encoding="utf-8", errors="replace") as fh:
                for n, line in enumerate(fh, 1):
                    for m in pat.finditer(line):
                        if not m.group(0).endswith("users.noreply.github.com"):
                            hits.append(f"{rel}:{n}: {m.group(0)}")
        self.assertEqual(hits, [])

    def test_no_absolute_user_paths(self):
        pat = re.compile(r"[A-Za-z]:\\+Users\\+|/Users/[A-Za-z]|/home/[a-z][a-z0-9_-]*/", re.I)
        hits = []
        for rel, full in text_files():
            with open(full, encoding="utf-8", errors="replace") as fh:
                for n, line in enumerate(fh, 1):
                    if len(line) < 5000 and pat.search(line):
                        hits.append(f"{rel}:{n}")
        self.assertEqual(hits, [])

    def test_license_is_mit_and_names_no_individual(self):
        text = h.read_text("LICENSE")
        self.assertTrue(text.startswith("MIT License"))
        self.assertRegex(text, r"Copyright \(c\) \d{4} .+ contributors")

    def test_third_party_license_texts_present(self):
        self.assertTrue(os.path.isfile(os.path.join(h.ROOT, "third_party_licenses", "Apache-2.0.txt")))
        notices = h.read_text("THIRD_PARTY_NOTICES.md")
        for component in ("SheetJS", "JSZip", "Bootstrap Icons", "Bootstrap"):
            self.assertIn(component, notices)


if __name__ == "__main__":
    unittest.main()
