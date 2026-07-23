"""Data models for :mod:`afriso`."""
from __future__ import annotations

import csv
import io
import json
from dataclasses import asdict, dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class Country:
    """An African country or territory."""

    code2: str  # ISO 3166-1 alpha-2, e.g. "NG"
    code3: str  # ISO 3166-1 alpha-3, e.g. "NGA"
    name: str  # English short name
    region: str  # e.g. "West Africa"
    language_count: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class Language:
    """A language spoken in Africa, keyed by its ISO 639-3 code."""

    iso639_3: str
    name: str
    alt_names: tuple[str, ...] = ()
    iso639_1: str | None = None  # 2-letter code, if any
    iso639_2b: str | None = None  # bibliographic 3-letter code
    iso639_2t: str | None = None  # terminological 3-letter code
    scope: str | None = None  # individual | macrolanguage | special
    type: str | None = None  # living | extinct | ancient | historical | ...
    glottocode: str | None = None
    family: str | None = None  # top-level Glottolog family name
    family_glottocode: str | None = None
    is_isolate: bool = False
    countries: tuple[str, ...] = ()  # ISO 3166-1 alpha-2 codes
    regions: tuple[str, ...] = ()
    macroareas: tuple[str, ...] = ()
    latitude: float | None = None
    longitude: float | None = None

    @property
    def code(self) -> str:
        """Alias for :attr:`iso639_3`."""
        return self.iso639_3

    def to_dict(self) -> dict:
        d = asdict(self)
        for key in ("alt_names", "countries", "regions", "macroareas"):
            d[key] = list(d[key])
        return d

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        return f"{self.name} [{self.iso639_3}]"


class LanguageSet(tuple):
    """An immutable, list-like collection of :class:`Language` objects.

    Supports chained filtering and export to common formats.
    """

    # -- filtering ---------------------------------------------------------
    def filter(self, predicate) -> "LanguageSet":
        return LanguageSet(x for x in self if predicate(x))

    def by_family(self, family: str) -> "LanguageSet":
        key = (family or "").strip().lower()
        return self.filter(lambda x: (x.family or "").lower() == key)

    def by_region(self, region: str) -> "LanguageSet":
        from .core import _canonical_region

        canon = _canonical_region(region)
        return self.filter(lambda x: canon in x.regions)

    def by_country(self, country: str) -> "LanguageSet":
        from .core import _canonical_country_code

        code2 = _canonical_country_code(country)
        return self.filter(lambda x: code2 in x.countries)

    def living(self) -> "LanguageSet":
        return self.filter(lambda x: x.type == "living")

    def sorted_by(self, attr: str = "name", reverse: bool = False) -> "LanguageSet":
        return LanguageSet(
            sorted(self, key=lambda x: (getattr(x, attr) or ""), reverse=reverse)
        )

    # -- projections -------------------------------------------------------
    def codes(self) -> list[str]:
        return [x.iso639_3 for x in self]

    def names(self) -> list[str]:
        return [x.name for x in self]

    def families(self) -> list[str]:
        return sorted({x.family for x in self if x.family})

    # -- export ------------------------------------------------------------
    def to_dicts(self) -> list[dict]:
        return [x.to_dict() for x in self]

    def to_json(self, path: str | None = None, indent: int = 2) -> str:
        text = json.dumps(self.to_dicts(), ensure_ascii=False, indent=indent)
        if path:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(text)
        return text

    def to_csv(
        self,
        path: str | None = None,
        columns: Iterable[str] | None = None,
        list_sep: str = "; ",
    ) -> str:
        cols = list(columns) if columns else [
            "iso639_3", "name", "alt_names", "iso639_1", "scope", "type",
            "glottocode", "family", "is_isolate", "countries", "regions",
        ]
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(cols)
        for x in self:
            row = []
            for c in cols:
                val = getattr(x, c, "")
                if isinstance(val, (list, tuple)):
                    val = list_sep.join(val)
                row.append("" if val is None else val)
            writer.writerow(row)
        text = buf.getvalue()
        if path:
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(text)
        return text

    def to_dataframe(self):
        """Return a :class:`pandas.DataFrame` (requires pandas)."""
        try:
            import pandas as pd
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "to_dataframe() requires pandas. Install with `pip install afriso[pandas]`."
            ) from exc
        return pd.DataFrame(self.to_dicts())

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        preview = ", ".join(str(x) for x in self[:3])
        more = f", ... +{len(self) - 3} more" if len(self) > 3 else ""
        return f"LanguageSet({len(self)} languages: {preview}{more})"
