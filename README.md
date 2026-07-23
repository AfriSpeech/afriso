# afriso 🌍

**Map African language names to ISO 639-3 codes, countries, families, and alternative names — and back.**

`afriso` is a small, dependency-free Python library for anyone working with
African languages in data-processing and NLP tasks. Look a language up by name,
alternative name, or code; filter by country, region, or language family; and
export the result to dicts, JSON, CSV, or a pandas DataFrame.

It covers **2,264 languages** spoken across **58 African countries and
territories**, grouped into **58 language families**, with alternative names for
**2,114** of them — including the widely-used **macrolanguage** codes (Swahili
`swa`, Akan `aka`, Oromo `orm`, Fulah `ful`, …).

Built entirely from open sources: the **SIL ISO 639-3** code tables and
**Glottolog** (CC-BY 4.0). No proprietary Ethnologue data.

## Install

```bash
pip install afriso              # core library, zero dependencies
pip install "afriso[pandas]"    # optional: enables .to_dataframe()
```

## Quick start

```python
import afriso

# Names <-> codes (case-insensitive; accepts names, alt names, and codes)
afriso.to_iso("Yoruba")        # 'yor'
afriso.to_iso("Yariba")        # 'yor'   (alternative name)
afriso.to_name("hau")          # 'Hausa'
afriso.to_name("sw")           # 'Swahili (macrolanguage)'  (ISO 639-1 works too)

# Full record
lang = afriso.get("Bambara")
lang.iso639_3       # 'bam'
lang.family         # 'Mande'
lang.countries      # ('CI', 'GN', 'ML', 'SN')
lang.regions        # ('West Africa',)
lang.alt_names      # ('Bamana', 'Bamanakan', 'Bamanankan')
lang.glottocode     # 'bamb1269'
```

## Filter & group

```python
afriso.by_country("Nigeria")            # LanguageSet of 568 languages
afriso.by_country("NG")                 # same — alpha-2, alpha-3, or name
afriso.by_region("West Africa")         # region grouping
afriso.by_family("Mande")               # by language family

# Chain filters
afriso.by_region("West Africa").by_family("Mande").names()
# ['Bambara', 'Bandi', 'Bankagooma', 'Beng', 'Bissa', 'Boko (Benin)', ...]

# Just the living languages of East Africa, as codes
afriso.by_region("East Africa").living().codes()
```

## Export in any format

Every query returns a `LanguageSet` with built-in exporters:

```python
langs = afriso.by_country("Ghana").sorted_by("name")

langs.codes()            # ['aae', 'ada', 'afu', ...]
langs.names()            # ['Adangme', 'Anufo', ...]
langs.to_dicts()         # list[dict]
langs.to_json("gh.json") # write JSON (also returns the string)
langs.to_csv("gh.csv")   # write CSV
langs.to_dataframe()     # pandas DataFrame (needs afriso[pandas])
```

## Explore the dimensions

```python
afriso.families(with_counts=True)   # [('Atlantic-Congo', 1378), ('Afro-Asiatic', 318), ...]
afriso.regions()                    # ['North Africa', 'West Africa', 'Central Africa', ...]
afriso.countries("East Africa")     # [Country(code2='BI', name='Burundi', ...), ...]
afriso.get_country("gh")            # Country(code2='GH', code3='GHA', name='Ghana', ...)
afriso.info()                       # dataset counts + source versions
```

## Command line

The same power from the shell — handy for pipelines:

```bash
afriso iso Yoruba                              # yor
afriso name hau                                # Hausa
afriso country Nigeria --format csv > ng.csv   # all NG languages as CSV
afriso region "West Africa" --family Mande     # chained filter
afriso family Atlantic-Congo --format codes    # just ISO codes
afriso families                                # families with counts
afriso search swahili                          # fuzzy name search
```

## Data model

Each `Language` has:

| Field | Description |
|-------|-------------|
| `iso639_3` | ISO 639-3 code (the key), e.g. `yor` |
| `name` | Reference (English) name |
| `alt_names` | Alternative names & spellings |
| `iso639_1` / `iso639_2b` / `iso639_2t` | Other ISO 639 codes, where they exist |
| `scope` | `individual`, `macrolanguage`, or `special` |
| `type` | `living`, `extinct`, `ancient`, `historical`, `constructed` |
| `glottocode` | Glottolog code |
| `family` | Top-level language family, e.g. `Atlantic-Congo` |
| `family_glottocode` | Glottolog code of the family |
| `is_isolate` | Whether the language is a genealogical isolate |
| `countries` | ISO 3166-1 alpha-2 codes where it is spoken |
| `regions` | African regions derived from `countries` |
| `macroareas` | Glottolog macroareas |
| `latitude` / `longitude` | Approximate centre of the speaker area |

Regions are the five common groupings: **North**, **West**, **Central**,
**East**, and **Southern Africa** (aliases like "Western Africa" are accepted).

## Data sources & licensing

The library code is MIT-licensed. The bundled data is derived from the SIL
ISO 639-3 code tables and **Glottolog v5.2 (CC-BY 4.0)** — see
[`DATA_LICENSE.md`](DATA_LICENSE.md) for attribution. Regenerate it any time
with:

```bash
python scripts/build_data.py
```

## Development

```bash
git clone https://github.com/AfriSpeech/afriso.git
cd afriso
pip install -e ".[dev]"
pytest
```
