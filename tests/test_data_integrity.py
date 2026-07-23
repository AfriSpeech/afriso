"""Structural validation of the dataset CSV.

These are the checks CI runs on every pull request. They verify that an edit to
data/languages.csv is *well-formed* — they do NOT (and cannot) judge whether an
edit is factually correct. That is what human review is for.
"""
import re

import afriso

ISO3_RE = re.compile(r"^[a-z]{3}$")
ISO1_RE = re.compile(r"^[a-z]{2}$")


def test_iso639_3_codes_are_wellformed():
    for lang in afriso.languages():
        assert ISO3_RE.match(lang.iso639_3), lang.iso639_3


def test_no_duplicate_codes():
    codes = afriso.languages().codes()
    dupes = {c for c in codes if codes.count(c) > 1}
    assert not dupes, f"duplicate ISO 639-3 codes: {sorted(dupes)}"


def test_required_fields_present():
    for lang in afriso.languages():
        assert lang.name.strip(), f"{lang.iso639_3} has an empty name"
        assert lang.scope, f"{lang.iso639_3} has no scope"


def test_iso639_1_wellformed_when_present():
    for lang in afriso.languages():
        if lang.iso639_1:
            assert ISO1_RE.match(lang.iso639_1), f"{lang.iso639_3}: {lang.iso639_1!r}"


def test_country_codes_are_known_african_codes():
    valid = {c.code2 for c in afriso.countries()}
    for lang in afriso.languages():
        bad = [c for c in lang.countries if c not in valid]
        assert not bad, f"{lang.iso639_3} has non-African/invalid countries: {bad}"


def test_alt_names_have_no_empty_entries():
    for lang in afriso.languages():
        assert all(a.strip() for a in lang.alt_names), lang.iso639_3
        # an alt name should never just duplicate the primary name
        assert lang.name.lower() not in {a.lower() for a in lang.alt_names}, lang.iso639_3


def test_scope_and_type_use_known_values():
    scopes = {"individual", "macrolanguage", "special"}
    types = {"living", "extinct", "ancient", "historical", "constructed", "special"}
    for lang in afriso.languages():
        assert lang.scope in scopes, f"{lang.iso639_3}: scope={lang.scope!r}"
        if lang.type:
            assert lang.type in types, f"{lang.iso639_3}: type={lang.type!r}"
