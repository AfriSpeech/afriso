"""Public query API for :mod:`afriso`."""
from __future__ import annotations

from collections import Counter

from . import _data
from .models import Country, Language, LanguageSet

# Region aliases (kept in sync with scripts/africa_countries.py).
_REGION_ALIASES = {
    "north africa": "North Africa",
    "northern africa": "North Africa",
    "west africa": "West Africa",
    "western africa": "West Africa",
    "central africa": "Central Africa",
    "middle africa": "Central Africa",
    "east africa": "East Africa",
    "eastern africa": "East Africa",
    "southern africa": "Southern Africa",
}


# --------------------------------------------------------------------------
# Normalisation helpers
# --------------------------------------------------------------------------
def _canonical_region(region: str) -> str:
    if not region:
        raise ValueError("region must be a non-empty string")
    key = region.strip().lower()
    if key in _REGION_ALIASES:
        return _REGION_ALIASES[key]
    raise ValueError(
        f"Unknown region {region!r}. Valid regions: {', '.join(regions())}."
    )


def _canonical_country_code(country: str) -> str:
    """Resolve a country name / alpha-2 / alpha-3 to its alpha-2 code."""
    if not country:
        raise ValueError("country must be a non-empty string")
    c = _data._country_index().get(country.strip().lower())
    if c is None:
        raise ValueError(
            f"Unknown African country {country!r}. "
            "Use an ISO 3166 alpha-2/alpha-3 code or English name."
        )
    return c.code2


# --------------------------------------------------------------------------
# Single-item lookup
# --------------------------------------------------------------------------
def get(key: str) -> Language | None:
    """Resolve a language by ISO 639-3/639-1 code, glottocode, name, or alt name.

    Matching is case-insensitive. Resolution order: ISO 639-3, glottocode,
    ISO 639-1, exact primary name, then alternative name. Returns ``None`` if
    nothing matches.
    """
    if not key:
        return None
    idx = _data._indexes()
    raw = key.strip()
    low = raw.lower()

    if raw in idx["by_code"]:
        return idx["by_code"][raw]
    if low in idx["by_glotto"]:
        return idx["by_glotto"][low]
    if low in idx["by_iso1"]:
        return idx["by_iso1"][low]
    if low in idx["by_name"]:
        return idx["by_name"][low][0]
    if low in idx["by_alt"]:
        return idx["by_alt"][low][0]
    return None


def to_iso(name: str) -> str | None:
    """Return the ISO 639-3 code for a language name (or ``None``)."""
    lang = get(name)
    return lang.iso639_3 if lang else None


def to_name(code: str) -> str | None:
    """Return the reference name for an ISO 639-3/639-1 code (or ``None``)."""
    lang = get(code)
    return lang.name if lang else None


def search(query: str, limit: int | None = None) -> LanguageSet:
    """Substring search across primary and alternative names (case-insensitive)."""
    q = (query or "").strip().lower()
    if not q:
        return LanguageSet()
    hits = []
    for lang in _data.all_languages():
        if q in lang.name.lower() or any(q in a.lower() for a in lang.alt_names):
            hits.append(lang)
    # exact / prefix matches first, then alphabetical
    hits.sort(key=lambda x: (x.name.lower() != q, not x.name.lower().startswith(q), x.name.lower()))
    if limit is not None:
        hits = hits[:limit]
    return LanguageSet(hits)


# --------------------------------------------------------------------------
# Collections & filtering
# --------------------------------------------------------------------------
def languages() -> LanguageSet:
    """Return all African languages."""
    return _data.all_languages()


def by_country(country: str) -> LanguageSet:
    """Languages spoken in a country (accepts alpha-2, alpha-3, or name)."""
    code2 = _canonical_country_code(country)
    return LanguageSet(x for x in _data.all_languages() if code2 in x.countries)


def by_region(region: str) -> LanguageSet:
    """Languages spoken in a region (e.g. ``"West Africa"``)."""
    canon = _canonical_region(region)
    return LanguageSet(x for x in _data.all_languages() if canon in x.regions)


def by_family(family: str) -> LanguageSet:
    """Languages belonging to a language family (e.g. ``"Atlantic-Congo"``)."""
    key = (family or "").strip().lower()
    if not key:
        raise ValueError("family must be a non-empty string")
    return LanguageSet(
        x for x in _data.all_languages() if (x.family or "").lower() == key
    )


# --------------------------------------------------------------------------
# Dimension listings
# --------------------------------------------------------------------------
def families(with_counts: bool = False):
    """List language families. Returns names, or ``[(name, count), ...]``."""
    counts = Counter(x.family for x in _data.all_languages() if x.family)
    if with_counts:
        return counts.most_common()
    return sorted(counts)


def regions() -> list[str]:
    """List the African regions used for filtering."""
    return ["North Africa", "West Africa", "Central Africa", "East Africa", "Southern Africa"]


def countries(region: str | None = None) -> list[Country]:
    """List African countries, optionally filtered by region."""
    out = list(_data.all_countries())
    if region is not None:
        canon = _canonical_region(region)
        out = [c for c in out if c.region == canon]
    return sorted(out, key=lambda c: c.name)


def get_country(key: str) -> Country | None:
    """Resolve a country by alpha-2, alpha-3, or English name."""
    if not key:
        return None
    return _data._country_index().get(key.strip().lower())


def info() -> dict:
    """Return dataset metadata (counts and source provenance)."""
    return dict(_data.meta())
