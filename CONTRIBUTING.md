# Contributing to afriso

Thank you for helping make African language data more accurate! The most
valuable contributions are **corrections to the language data** — especially
alternative names, families, and countries.

## The data is one CSV file

Everything lives in **[`src/afriso/data/languages.csv`](src/afriso/data/languages.csv)**,
one row per language. It is plain CSV so you can edit it in any spreadsheet or
text editor and see a clean diff in your pull request.

### Columns

| Column | Notes |
|--------|-------|
| `iso639_3` | ISO 639-3 code — the key. **Don't change this.** |
| `name` | Reference (English) name |
| `alt_names` | Other names & spellings, separated by `;` |
| `iso639_1`, `iso639_2b`, `iso639_2t` | Other ISO 639 codes (may be empty) |
| `scope` | `individual`, `macrolanguage`, or `special` |
| `type` | `living`, `extinct`, `ancient`, `historical`, `constructed` |
| `glottocode`, `family`, `family_glottocode` | Classification |
| `is_isolate` | `true` or `false` |
| `countries` | ISO 3166-1 alpha-2 codes, separated by `;` (e.g. `GH;TG`) |
| `latitude`, `longitude` | Optional coordinates |

> **Regions** (West Africa, East Africa, …) are **not** a column — they are
> derived automatically from `countries`, so you never edit them directly.

## Common corrections

**Add or fix an alternative name.** Edit the `alt_names` cell; separate names
with `;`. Example — adding the Twi dialect names:

```
twi,Twi,Akuapem;Akuapem Twi;Asante;Asante Twi,tw,...
```

Please add **real names** — endonyms speakers actually use, well-known dialect
names, or attested spellings. If you're removing a name because it's an
inaccurate/archaic exonym, say so in your PR description.

**Fix a country or family.** Edit the `countries` (or `family`) cell. Keep
country codes as valid ISO 3166-1 alpha-2 codes for African countries (see
`src/afriso/data/countries.csv`).

## Before you open a PR

Run the test suite — it validates that the CSV still loads and that regions,
countries, and lookups stay consistent:

```bash
pip install -e ".[dev]"
pytest
```

## Adding languages from upstream

You normally don't need to. Maintainers can pull newly-published SIL/Glottolog
languages with an **additive** refresh that never overwrites curated rows:

```bash
python scripts/seed_data.py --dry-run   # preview additions
python scripts/seed_data.py             # append new rows only
```

## Data provenance

The dataset is seeded from the SIL ISO 639-3 tables and Glottolog (CC-BY 4.0),
then improved by contributors. See [`DATA_LICENSE.md`](DATA_LICENSE.md).
