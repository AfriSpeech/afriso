"""Lazy loading and indexing of the bundled datasets."""
from __future__ import annotations

import json
from collections import defaultdict
from functools import lru_cache

try:  # Python 3.9+
    from importlib.resources import files
except ImportError:  # pragma: no cover
    from importlib_resources import files  # type: ignore

from .models import Country, Language, LanguageSet

_LIST_FIELDS = ("alt_names", "countries", "regions", "macroareas")


def _read(name: str):
    with (files("afriso.data") / name).open("r", encoding="utf-8") as fh:
        return json.load(fh)


@lru_cache(maxsize=1)
def all_languages() -> LanguageSet:
    out = []
    for row in _read("languages.json"):
        row = dict(row)
        for f in _LIST_FIELDS:
            row[f] = tuple(row.get(f) or ())
        out.append(Language(**row))
    return LanguageSet(out)


@lru_cache(maxsize=1)
def all_countries() -> tuple[Country, ...]:
    return tuple(Country(**row) for row in _read("countries.json"))


@lru_cache(maxsize=1)
def meta() -> dict:
    return _read("meta.json")


@lru_cache(maxsize=1)
def _indexes():
    """Build lookup indexes over the language table."""
    langs = all_languages()
    by_code: dict[str, Language] = {}
    by_glotto: dict[str, Language] = {}
    by_name: dict[str, list[Language]] = defaultdict(list)  # exact primary name
    by_alt: dict[str, list[Language]] = defaultdict(list)  # any alt name
    by_iso1: dict[str, Language] = {}

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
        "by_code": by_code,
        "by_glotto": by_glotto,
        "by_name": dict(by_name),
        "by_alt": dict(by_alt),
        "by_iso1": by_iso1,
    }


@lru_cache(maxsize=1)
def _country_index():
    idx: dict[str, Country] = {}
    for c in all_countries():
        idx[c.code2.lower()] = c
        idx[c.code3.lower()] = c
        idx[c.name.lower()] = c
    return idx
