# Examples

`messages/` contains two small **synthetic** messages (all identifiers are placeholders) that show the two
shapes the generator writes:

| File | Service | Contains |
|---|---|---|
| `messages/1_device-post.xml` | `DEVICE.POST` | two `device:Device` entries, each creating a **new** Basic UDI-DI together with its first UDI-DI |
| `messages/2_udi-di-post.xml` | `UDI_DI.POST` | three `device:UDIDIData` entries adding further UDI-DIs to those Basic UDI-DIs |

They were assembled with `tests/fixtures.py` (a model of the generator's output format) and validated against
the official XSD schemas; `tests/test_check_xml.py` checks that the files and the fixtures stay in sync. They
show the structure - for real submissions use the files the application produces.

Check them yourself:

```bash
python tools/check_xml.py examples/messages/*.xml
python tools/check_xml.py --xsd-dir /path/to/dtx-schemas examples/messages/*.xml
```

The checker prints a warning about the access token: the examples carry the placeholder the application writes
when no token was entered. Replace it with your token before uploading real files.
