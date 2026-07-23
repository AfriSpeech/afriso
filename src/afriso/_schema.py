"""Shared schema and (de)serialisation for the CSV dataset.

The dataset in ``src/afriso/data/languages.csv`` is the source of truth. It is
plain CSV so that anyone can read and correct it in a pull request. This module
defines the columns and how list-valued cells are encoded, and is used by both
the runtime loader (``_data.py``) and the seeder (``scripts/seed_data.py``).
"""
from __future__ import annotations

# Columns of languages.csv, in order. `regions` is intentionally NOT stored —
# it is derived from `countries` at load time so it can never drift.
LANGUAGE_COLUMNS = [
    "iso639_3",          # ISO 639-3 code (the key), e.g. "yor"
    "name",              # reference / English name
    "alt_names",         # other names & spellings (see LIST_SEP)
    "iso639_1",          # ISO 639-1 2-letter code, if any
    "iso639_2b",         # ISO 639-2 bibliographic code, if any
    "iso639_2t",         # ISO 639-2 terminological code, if any
    "scope",             # individual | macrolanguage | special
    "type",              # living | extinct | ancient | historical | constructed
    "glottocode",        # Glottolog code
    "family",            # top-level language family, e.g. "Atlantic-Congo"
    "family_glottocode",
    "is_isolate",        # true | false
    "countries",         # ISO 3166-1 alpha-2 codes (see LIST_SEP)
    "latitude",
    "longitude",
]

COUNTRY_COLUMNS = ["code2", "code3", "name", "region"]

LIST_SEP = ";"


def join_list(values) -> str:
    return LIST_SEP.join(values or ())


def split_list(cell: str):
    if not cell:
        return []
    return [v.strip() for v in cell.split(LIST_SEP) if v.strip()]


def language_to_row(lang: dict) -> dict:
    """Serialise a language dict to a CSV row (all str values)."""
    row = {}
    for col in LANGUAGE_COLUMNS:
        val = lang.get(col)
        if col in ("alt_names", "countries"):
            val = join_list(val)
        elif col == "is_isolate":
            val = "true" if val else "false"
        elif val is None:
            val = ""
        row[col] = str(val)
    return row


def row_to_language(row: dict) -> dict:
    """Parse a CSV row into a normalised language dict (typed values)."""
    def num(v):
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    return {
        "iso639_3": row["iso639_3"].strip(),
        "name": row["name"].strip(),
        "alt_names": tuple(split_list(row.get("alt_names", ""))),
        "iso639_1": (row.get("iso639_1") or "").strip() or None,
        "iso639_2b": (row.get("iso639_2b") or "").strip() or None,
        "iso639_2t": (row.get("iso639_2t") or "").strip() or None,
        "scope": (row.get("scope") or "").strip() or None,
        "type": (row.get("type") or "").strip() or None,
        "glottocode": (row.get("glottocode") or "").strip() or None,
        "family": (row.get("family") or "").strip() or None,
        "family_glottocode": (row.get("family_glottocode") or "").strip() or None,
        "is_isolate": (row.get("is_isolate") or "").strip().lower() == "true",
        "countries": tuple(split_list(row.get("countries", ""))),
        "latitude": num(row.get("latitude")),
        "longitude": num(row.get("longitude")),
    }
