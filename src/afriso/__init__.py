"""afriso — map African language names to ISO 639-3 codes, countries & families.

A small, dependency-free toolkit for people working with African languages in
data-processing tasks. Look languages up by name, alternative name, or code;
filter by country, region, or language family; and export the result to dicts,
JSON, CSV, or a pandas DataFrame.

Data is built from open sources: the SIL ISO 639-3 code tables and Glottolog
(CC-BY 4.0). See ``afriso.info()`` for versions.

Quick start
-----------
>>> import afriso
>>> afriso.to_iso("Yoruba")
'yor'
>>> afriso.to_name("hau")
'Hausa'
>>> afriso.get("Twi").family
'Atlantic-Congo'
>>> len(afriso.by_country("Nigeria"))          # doctest: +SKIP
>>> afriso.by_region("West Africa").by_family("Mande").names()  # doctest: +SKIP
>>> afriso.by_country("GH").to_csv("ghana_languages.csv")       # doctest: +SKIP
"""
from .core import (
    by_country,
    by_family,
    by_region,
    countries,
    families,
    get,
    get_country,
    info,
    languages,
    regions,
    search,
    to_iso,
    to_name,
)
from .models import Country, Language, LanguageSet

__version__ = "1.0.0"

__all__ = [
    "get",
    "to_iso",
    "to_name",
    "search",
    "languages",
    "by_country",
    "by_region",
    "by_family",
    "families",
    "regions",
    "countries",
    "get_country",
    "info",
    "Language",
    "Country",
    "LanguageSet",
    "__version__",
]
