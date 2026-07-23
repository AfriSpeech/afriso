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

## The dataset

`src/afriso/data/languages.csv` is **seeded** from the sources above by
`scripts/seed_data.py` and then **curated by hand** via pull requests (see
`CONTRIBUTING.md`). The seeder is additive — re-running it only appends
newly-published upstream languages and never overwrites curated rows:

```bash
python scripts/seed_data.py --dry-run   # preview additions
python scripts/seed_data.py             # append new rows only
```

If you redistribute the bundled data, retain the Glottolog CC-BY attribution.
