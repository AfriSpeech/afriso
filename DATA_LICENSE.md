# Data sources & licenses

`afriso` bundles a dataset (`src/afriso/data/`) built from the following open
sources. The `afriso` code is MIT-licensed; the data remains subject to the
licenses below.

## SIL ISO 639-3 code tables

- **What:** language codes, reference names, ISO 639-1/639-2 mappings, scope
  (individual / macrolanguage / special), language type, alternative print
  names, and macrolanguage membership.
- **Source:** <https://iso639-3.sil.org/code_tables/download_tables>
- **Terms:** The ISO 639-3 code set is maintained by SIL International as the
  ISO 639-3 Registration Authority and made freely available for use.

## Glottolog

- **What:** glottocodes, language-family classification, countries of use,
  macroareas, coordinates, and additional alternative names.
- **Version:** Glottolog v5.2 (via the `glottolog-cldf` release).
- **Source:** <https://glottolog.org> · <https://github.com/glottolog/glottolog-cldf>
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0).
- **Attribution:** Hammarström, Harald & Forkel, Robert & Haspelmath, Martin &
  Bank, Sebastian. *Glottolog.* Max Planck Institute for Evolutionary
  Anthropology.

## Regenerating the data

The bundled files are produced by `scripts/build_data.py`, which downloads the
sources above and writes `languages.json`, `countries.json`, and `meta.json`
into `src/afriso/data/`. Run:

```bash
python scripts/build_data.py
```

If you redistribute the bundled data, retain the Glottolog CC-BY attribution.
