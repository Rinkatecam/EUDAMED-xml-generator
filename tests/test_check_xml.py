"""Tests for tools/check_xml.py - one positive and one negative case per documented portal rule."""
import glob
import os
import tempfile
import unittest

import helpers as h
import check_xml
import fixtures as fx

K = fx.rich_kwargs  # storage (ANY) + warning (EN) + market data, as the generator writes them


def errors(xml):
    return [m for s, m in check_xml.check_message(xml.encode("utf-8")) if s == check_xml.ERROR]


def warnings(xml):
    return [m for s, m in check_xml.check_message(xml.encode("utf-8")) if s == check_xml.WARNING]


def good_device_post():
    return fx.push(fx.device_entity("+EXAMPLE000011X", "++EXAMPLE00001AA", **K()))


def good_udi_di_post():
    return fx.push(fx.udidi_entity("+EXAMPLE000012Y", "++EXAMPLE00001AA", **K()),
                   service=("UDI_DI", "POST"), narrow=True)


class TestAcceptedMessages(unittest.TestCase):
    def test_device_post_is_clean(self):
        self.assertEqual(errors(good_device_post()), [])

    def test_udi_di_post_is_clean(self):
        self.assertEqual(errors(good_udi_di_post()), [])

    def test_messages_without_optional_blocks_are_clean(self):
        self.assertEqual(errors(fx.push(fx.device_entity("+EXAMPLE000011X", "++EXAMPLE00001AA"))), [])

    def test_placeholder_token_is_only_a_warning(self):
        xml = good_device_post()
        self.assertEqual(errors(xml), [])
        self.assertTrue(any("token" in w for w in warnings(xml)))
        self.assertEqual(warnings(fx.push(fx.device_entity("+EXAMPLE000011X", "++EXAMPLE00001AA"), token="abc123")), [])

    def test_300_entities_are_allowed(self):
        payload = "".join(fx.udidi_entity(f"+EXAMPLE{i:06d}X", "++EXAMPLE00001AA") for i in range(300))
        self.assertEqual(errors(fx.push(payload, service=("UDI_DI", "POST"), narrow=True)), [])


class TestRejectedMessages(unittest.TestCase):
    def assertHasError(self, xml, fragment):
        errs = errors(xml)
        self.assertTrue(any(fragment in e for e in errs), f"no error containing {fragment!r} in {errs}")

    def test_not_well_formed(self):
        self.assertHasError("<m:Push", "not well-formed")

    def test_wrong_root(self):
        self.assertHasError('<?xml version="1.0"?><root/>', "expected a Push")

    def test_wrong_version(self):
        self.assertHasError(fx.push(fx.device_entity("+EXAMPLE000011X", "++EXAMPLE00001AA"), version="3.0.25"),
                            'version="3.0.25"')

    def test_service_does_not_match_payload(self):
        # UDI-DI entities sent with the DEVICE service (portal error ERR-DTX-EUD-103.03-02 territory)
        xml = fx.push(fx.udidi_entity("+EXAMPLE000012Y", "++EXAMPLE00001AA"), service=("DEVICE", "POST"))
        self.assertHasError(xml, "<recipient> service is DEVICE.POST but the payload requires UDI_DI.POST")
        self.assertHasError(xml, "<sender> service is DEVICE.POST")

    def test_sender_block_mismatch_alone_is_caught(self):
        xml = fx.push(fx.device_entity("+EXAMPLE000011X", "++EXAMPLE00001AA"), sender_service=("UDI_DI", "POST"))
        errs = errors(xml)
        self.assertEqual(len(errs), 1)
        self.assertIn("<sender>", errs[0])

    def test_wrong_operation(self):
        xml = fx.push(fx.device_entity("+EXAMPLE000011X", "++EXAMPLE00001AA"), service=("DEVICE", "PATCH"))
        self.assertHasError(xml, "DEVICE.PATCH but the payload requires DEVICE.POST")

    def test_mixed_payload(self):
        xml = fx.push(fx.device_entity("+EXAMPLE000011X", "++EXAMPLE00001AA")
                      + fx.udidi_entity("+EXAMPLE000012Y", "++EXAMPLE00001AA"))
        self.assertHasError(xml, "mixes")

    def test_more_than_300_entities(self):
        payload = "".join(fx.udidi_entity(f"+EXAMPLE{i:06d}X", "++EXAMPLE00001AA") for i in range(301))
        self.assertHasError(fx.push(payload, service=("UDI_DI", "POST"), narrow=True), "301 entities")

    def test_empty_payload(self):
        self.assertHasError(fx.push(""), "payload is empty")

    def test_same_basic_udi_declared_twice(self):
        # The exact shape EUDAMED rejects with "device identifier code ... already exists".
        xml = fx.push(fx.device_entity("+EXAMPLE000011X", "++EXAMPLE00001AA")
                      + fx.device_entity("+EXAMPLE000012Y", "++EXAMPLE00001AA"))
        self.assertHasError(xml, "Basic UDI-DI ++EXAMPLE00001AA (HIBCC) is declared by 2")

    def test_distinct_basic_udis_in_one_message_are_fine(self):
        xml = fx.push(fx.device_entity("+EXAMPLE000011X", "++EXAMPLE00001AA")
                      + fx.device_entity("+EXAMPLE000021Y", "++EXAMPLE00002BB"))
        self.assertEqual(errors(xml), [])

    def test_comment_without_language(self):
        xml = good_device_post().replace("<lsn:language>ANY</lsn:language>\n", "", 1)
        self.assertHasError(xml, "without <lsn:language> (ERR-DTX-UDI-094.05-01)")

    def test_coded_storage_condition_with_real_language(self):
        xml = fx.push(fx.device_entity("+EXAMPLE000011X", "++EXAMPLE00001AA",
                                       storage=fx.storage_block(lang="EN")))
        self.assertHasError(xml, "ERR-DTX-UDI-028.05-03")

    def test_free_text_storage_code_needs_a_real_language(self):
        ok = fx.push(fx.device_entity("+EXAMPLE000011X", "++EXAMPLE00001AA",
                                      storage=fx.storage_block(lang="EN", code="SHC099")))
        bad = fx.push(fx.device_entity("+EXAMPLE000011X", "++EXAMPLE00001AA",
                                       storage=fx.storage_block(lang="ANY", code="SHC099")))
        self.assertEqual(errors(ok), [])
        self.assertHasError(bad, "ERR-DTX-UDI-028.05-03")

    def test_cw999_language_rule(self):
        ok = fx.push(fx.device_entity("+EXAMPLE000011X", "++EXAMPLE00001AA", warnings=fx.warnings_block(lang="EN")))
        bad = fx.push(fx.device_entity("+EXAMPLE000011X", "++EXAMPLE00001AA", warnings=fx.warnings_block(lang="ANY")))
        self.assertEqual(errors(ok), [])
        self.assertHasError(bad, "critical warning(s) with the wrong comment language")


class TestExampleMessages(unittest.TestCase):
    def test_examples_exist_and_pass(self):
        paths = sorted(glob.glob(os.path.join(h.ROOT, "examples", "messages", "*.xml")))
        self.assertEqual(len(paths), 2)
        for p in paths:
            with self.subTest(file=os.path.basename(p)):
                with open(p, "rb") as fh:
                    self.assertEqual([m for s, m in check_xml.check_message(fh.read()) if s == check_xml.ERROR], [])

    def test_examples_equal_the_fixture_output(self):
        # keeps the published examples from drifting away from the builders the tests rely on
        for name, builder in (("1_device-post.xml", fx.example_device_post), ("2_udi-di-post.xml", fx.example_udi_di_post)):
            with self.subTest(file=name):
                self.assertEqual(h.read_text(f"examples/messages/{name}"), builder())

    def test_cli_exit_codes(self):
        good = os.path.join(h.ROOT, "examples", "messages", "1_device-post.xml")
        with tempfile.TemporaryDirectory() as tmp:
            bad = os.path.join(tmp, "bad.xml")
            with open(bad, "w", encoding="utf-8") as fh:
                fh.write(fx.push(fx.device_entity("+EXAMPLE000011X", "++EXAMPLE00001AA"), version="0.0.0"))
            self.assertEqual(check_xml.main([good]), 0)
            self.assertEqual(check_xml.main([bad]), 1)
            self.assertEqual(check_xml.main([os.path.join(tmp, "missing.xml")]), 1)


XSD_DIR = os.environ.get("EUDAMED_XSD_DIR", "")


@unittest.skipUnless(XSD_DIR and os.path.isfile(os.path.join(XSD_DIR, "service", "Message.xsd")),
                     "set EUDAMED_XSD_DIR to a directory containing service/Message.xsd to run the XSD tests")
class TestAgainstTheOfficialSchema(unittest.TestCase):
    def validate(self, xml):
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "m.xml")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(xml)
            return check_xml.validate_xsd(p, XSD_DIR)

    def test_examples_are_schema_valid(self):
        for p in sorted(glob.glob(os.path.join(h.ROOT, "examples", "messages", "*.xml"))):
            with self.subTest(file=os.path.basename(p)):
                self.assertEqual(check_xml.validate_xsd(p, XSD_DIR), [])

    def test_wrong_version_is_schema_invalid(self):
        self.assertTrue(self.validate(fx.push(fx.device_entity("+EXAMPLE000011X", "++EXAMPLE00001AA"), version="3.0.25")))

    def test_mixed_payload_is_schema_invalid(self):
        xml = fx.push(fx.device_entity("+EXAMPLE000011X", "++EXAMPLE00001AA")
                      + fx.udidi_entity("+EXAMPLE000012Y", "++EXAMPLE00001AA"))
        self.assertTrue(self.validate(xml))

    def test_documented_portal_only_rules_are_invisible_to_the_schema(self):
        """The reason this tool exists: these messages are schema-VALID but rejected by the portal."""
        twice = fx.push(fx.device_entity("+EXAMPLE000011X", "++EXAMPLE00001AA")
                        + fx.device_entity("+EXAMPLE000012Y", "++EXAMPLE00001AA"))
        wrong_lang = fx.push(fx.device_entity("+EXAMPLE000011X", "++EXAMPLE00001AA", storage=fx.storage_block(lang="EN")))
        for name, xml in (("same Basic UDI twice", twice), ("EN on a coded storage condition", wrong_lang)):
            with self.subTest(case=name):
                self.assertEqual(self.validate(xml), [], "expected to be schema-valid")
                self.assertTrue(errors(xml), "but the portal-rule checker must flag it")


if __name__ == "__main__":
    unittest.main()
