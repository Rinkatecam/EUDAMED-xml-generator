# Third-party notices

`eudamed-xml-generator.html` is a single self-contained file. To make that possible it embeds
the following third-party components **unmodified** (minified) so that the tool works offline.
They keep their own licenses; the project's MIT license (see `LICENSE`) applies only to the
original code of this repository.

| Component | Version | License | Notice in the bundled file |
|---|---|---|---|
| [SheetJS Community Edition](https://sheetjs.com/) (`xlsx`) | 0.18.5 | Apache-2.0 | `xlsx.js (C) 2013-present SheetJS` |
| [JSZip](https://stuk.github.io/jszip/) | 3.10.1 | MIT (JSZip is dual licensed MIT or GPL-3.0-or-later; this project uses it under MIT) | `(c) 2009-2016 Stuart Knightley and contributors` |
| [pako](https://github.com/nodeca/pako) (bundled inside JSZip) | as bundled with JSZip 3.10.1 | MIT (contains code derived from zlib, zlib license) | referenced in the JSZip banner |
| [Bootstrap](https://getbootstrap.com/) (CSS only) | 5.3.3 | MIT | `Copyright 2011-2024 The Bootstrap Authors` |
| [Bootstrap Icons](https://icons.getbootstrap.com/) (CSS + embedded WOFF2 font) | 1.11.3 | MIT | `Copyright 2019-2024 The Bootstrap Authors` |

## License texts

* **Apache License 2.0** (SheetJS): the full, unmodified text is in
  [`third_party_licenses/Apache-2.0.txt`](third_party_licenses/Apache-2.0.txt).
* **MIT License** (JSZip, pako, Bootstrap, Bootstrap Icons): each upstream project publishes its own
  MIT license file with its exact copyright line; please refer to the upstream repositories linked above
  (e.g. `https://github.com/Stuk/jszip/blob/main/LICENSE.markdown`,
  `https://github.com/nodeca/pako/blob/main/LICENSE`,
  `https://github.com/twbs/bootstrap/blob/main/LICENSE`,
  `https://github.com/twbs/icons/blob/main/LICENSE`).
  The standard MIT license text is reproduced in this repository's `LICENSE` file.

## What is deliberately *not* bundled

* **EUDAMED XSD schemas and sample messages** are published by the European Commission and are not
  redistributed here. See the README for where to obtain them; the optional XSD tests and the
  `tools/check_xml.py` helper read them from a local directory you provide.
* No web fonts are bundled or loaded: the interface falls back to the fonts installed on your system.
