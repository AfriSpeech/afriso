"""Lazy loading and indexing of the bundled CSV dataset."""
from __future__ import annotations

import csv
from collections import defaultdict
from functools import lru_cache

try:  # Python 3.9+
    from importlib.resources import files
except ImportError:  # pragma: no cover
    from importlib_resources import files  # type: ignore

from ._schema import row_to_language
from .models import Country, Language, LanguageSet

GLOTTOLOG_VERSION = "v5.2"


def _open(name: str):
    return (files("afriso.data") / name).open("r", encoding="utf-8", newline="")


@lru_cache(maxsize=1)
def all_countries() -> tuple[Country, ...]:
    with _open("countries.csv") as fh:
        rows = list(csv.DictReader(fh))
    counts = _country_language_counts()
    return tuple(
        Country(
            code2=r["code2"], code3=r["code3"], name=r["name"],
            region=r["region"], language_count=counts.get(r["code2"], 0),
        )
        for r in rows
    )


@lru_cache(maxsize=1)
def _region_by_country() -> dict:
    with _open("countries.csv") as fh:
        return {r["code2"]: r["region"] for r in csv.DictReader(fh)}


@lru_cache(maxsize=1)
def _country_language_counts() -> dict:
    counts: dict[str, int] = defaultdict(int)
    with _open("languages.csv") as fh:
        for row in csv.DictReader(fh):
            for c in row.get("countries", "").split(";"):
                c = c.strip()
                if c:
                    counts[c] += 1
    return dict(counts)


@lru_cache(maxsize=1)
def all_languages() -> LanguageSet:
    region_map = _region_by_country()
    out = []
    with _open("languages.csv") as fh:
        for row in csv.DictReader(fh):
            data = row_to_language(row)
            data["regions"] = tuple(
                sorted({region_map[c] for c in data["countries"] if c in region_map})
            )
            out.append(Language(**data))
    return LanguageSet(out)


@lru_cache(maxsize=1)
def meta() -> dict:
    langs = all_languages()
    return {
        "language_count": len(langs),
        "country_count": len(all_countries()),
        "sources": {
            "iso639_3": "SIL ISO 639-3 code tables (iso639-3.sil.org)",
            "glottolog": f"Glottolog {GLOTTOLOG_VERSION} (CC-BY 4.0)",
        },
    }


@lru_cache(maxsize=1)
def _indexes():
    langs = all_languages()
    by_code, by_glotto, by_iso1 = {}, {}, {}
    by_name = defaultdict(list)
    by_alt = defaultdict(list)
    for lang in langs:
        by_code[lang.iso639_3] = lang
        if lang.glottocode:
            by_glotto[lang.glottocode] = lang
        if lang.iso639_1:
            by_iso1[lang.iso639_1.lower()] = lang
        by_name[lang.name.lower()].append(lang)
        for alt in lang.alt_names:
            by_alt[alt.lower()].append(lang)
    return {
        "by_code": by_code, "by_glotto": by_glotto,
        "by_name": dict(by_name), "by_alt": dict(by_alt), "by_iso1": by_iso1,
    }


@lru_cache(maxsize=1)
def _country_index():
    idx: dict[str, Country] = {}
    for c in all_countries():
        idx[c.code2.lower()] = c
        idx[c.code3.lower()] = c
        idx[c.name.lower()] = c
    return idx
