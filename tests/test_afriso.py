"""Tests for the afriso public API."""
import csv
import io
import json

import pytest

import afriso


# -- single lookup ---------------------------------------------------------
def test_to_iso_by_name():
    assert afriso.to_iso("Yoruba") == "yor"
    assert afriso.to_iso("hausa") == "hau"  # case-insensitive


def test_to_name_by_code():
    assert afriso.to_name("yor") == "Yoruba"
    assert afriso.to_name("sw") == afriso.to_name("swa")  # 639-1 == 639-3


def test_get_resolution_paths():
    yor = afriso.get("yor")
    assert yor is afriso.get("Yoruba")
    assert afriso.get(yor.glottocode).iso639_3 == "yor"
    assert yor.code == "yor"


def test_get_by_alt_name():
    lang = afriso.get("Yariba")  # alternative name of Yoruba
    assert lang is not None and lang.iso639_3 == "yor"


def test_unknown_returns_none():
    assert afriso.get("Klingon") is None
    assert afriso.to_iso("definitely-not-a-language") is None


def test_macrolanguages_present():
    for code in ("swa", "aka", "orm", "ful", "mlg"):
        lang = afriso.get(code)
        assert lang is not None, code
        assert lang.scope == "macrolanguage"
        assert lang.countries  # aggregated from members / Glottolog


def test_macrolanguage_member_inherits_country():
    twi = afriso.get("Twi")
    assert "GH" in twi.countries  # inherited from the Akan macrolanguage
    assert twi in afriso.by_country("Ghana")


# -- fields ----------------------------------------------------------------
def test_language_has_family_and_countries():
    hau = afriso.get("Hausa")
    assert hau.family == "Afro-Asiatic"
    assert "NG" in hau.countries
    assert "West Africa" in hau.regions
    assert hau.alt_names  # non-empty


# -- search ----------------------------------------------------------------
def test_search_substring():
    hits = afriso.search("swahili")
    assert any(l.iso639_3 == "swa" for l in hits)


def test_search_ranks_exact_first():
    hits = afriso.search("Zulu")
    assert hits[0].name.lower().startswith("zulu")


# -- filtering -------------------------------------------------------------
def test_by_country_accepts_code_and_name():
    a = afriso.by_country("NG")
    b = afriso.by_country("Nigeria")
    c = afriso.by_country("NGA")
    assert set(a.codes()) == set(b.codes()) == set(c.codes())
    assert len(a) > 100


def test_by_region():
    west = afriso.by_region("West Africa")
    assert afriso.get("Yoruba") in west
    # region aliases work
    assert set(afriso.by_region("Western Africa").codes()) == set(west.codes())


def test_by_family():
    mande = afriso.by_family("Mande")
    assert len(mande) > 10
    assert all(l.family == "Mande" for l in mande)


def test_chained_filtering():
    result = afriso.by_region("West Africa").by_family("Mande")
    assert len(result) >= 1
    assert all("West Africa" in l.regions and l.family == "Mande" for l in result)


def test_invalid_region_and_country_raise():
    with pytest.raises(ValueError):
        afriso.by_region("Atlantis")
    with pytest.raises(ValueError):
        afriso.by_country("Narnia")


# -- listings --------------------------------------------------------------
def test_families_and_regions():
    fams = afriso.families()
    assert "Atlantic-Congo" in fams
    counts = dict(afriso.families(with_counts=True))
    assert counts["Atlantic-Congo"] > 100
    assert len(afriso.regions()) == 5


def test_countries():
    all_c = afriso.countries()
    assert len(all_c) >= 54
    west = afriso.countries(region="West Africa")
    assert any(c.name == "Nigeria" for c in west)
    assert afriso.get_country("gh").name == "Ghana"


# -- export ----------------------------------------------------------------
def test_export_json_and_dicts():
    data = afriso.by_country("Ghana")
    dicts = data.to_dicts()
    assert isinstance(dicts, list) and "iso639_3" in dicts[0]
    parsed = json.loads(data.to_json())
    assert len(parsed) == len(data)


def test_export_csv():
    text = afriso.by_family("Mande").to_csv()
    rows = list(csv.reader(io.StringIO(text)))
    assert rows[0][0] == "iso639_3"
    assert len(rows) - 1 == len(afriso.by_family("Mande"))


def test_export_csv_to_file(tmp_path):
    p = tmp_path / "out.csv"
    afriso.by_country("GH").to_csv(str(p))
    assert p.exists() and p.read_text().count("\n") > 1


def test_dataframe_roundtrip():
    df = afriso.by_country("Kenya").to_dataframe()
    assert len(df) == len(afriso.by_country("Kenya"))
    assert "family" in df.columns


# -- info ------------------------------------------------------------------
def test_info_metadata():
    meta = afriso.info()
    assert meta["language_count"] > 2000
    assert "glottolog" in meta["sources"]
