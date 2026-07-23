#!/usr/bin/env python3
"""Build the bundled ``afriso`` datasets from open sources.

Sources
-------
* SIL ISO 639-3 code tables (public):
    - iso-639-3.tab            -> codes, reference names, ISO 639-1/2, scope, type
    - iso-639-3_Name_Index.tab -> alternative / inverted print names
* Glottolog (CC-BY 4.0), glottolog-cldf release:
    - cldf/languages.csv       -> glottocode, family, countries, macroarea, coords

A language is treated as *African* when Glottolog places it (fully or partly)
in the Africa macroarea, or when any of the countries it is spoken in is an
African country per ``africa_countries.AFRICA``.

Outputs (written into src/afriso/data/):
    languages.json   - the enriched language table
    countries.json   - the African country reference table
    meta.json        - source versions / provenance

Run:  python scripts/build_data.py
"""
from __future__ import annotations

import csv
import io
import json
import os
import sys
import urllib.request
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW = os.path.join(ROOT, "data_sources")
OUT = os.path.join(ROOT, "src", "afriso", "data")

sys.path.insert(0, HERE)
from africa_countries import AFRICA  # noqa: E402

GLOTTOLOG_VERSION = "v5.2"
SIL_BASE = "https://iso639-3.sil.org/sites/iso639-3/files/downloads"
SOURCES = {
    "iso-639-3.tab": f"{SIL_BASE}/iso-639-3.tab",
    "iso-639-3_Name_Index.tab": f"{SIL_BASE}/iso-639-3_Name_Index.tab",
    "iso-639-3-macrolanguages.tab": f"{SIL_BASE}/iso-639-3-macrolanguages.tab",
    "glottolog_languages.csv": (
        "https://raw.githubusercontent.com/glottolog/glottolog-cldf/"
        f"{GLOTTOLOG_VERSION}/cldf/languages.csv"
    ),
    "glottolog_names.csv": (
        "https://raw.githubusercontent.com/glottolog/glottolog-cldf/"
        f"{GLOTTOLOG_VERSION}/cldf/names.csv"
    ),
}

# Junk tokens that appear as "names" in aggregated sources.
_NAME_JUNK = {"not specified", "unnamed", "undetermined", "unknown", ""}

SCOPE_LABELS = {"I": "individual", "M": "macrolanguage", "S": "special"}
TYPE_LABELS = {
    "L": "living",
    "E": "extinct",
    "A": "ancient",
    "H": "historical",
    "C": "constructed",
    "S": "special",
}


def fetch(name: str, url: str) -> str:
    """Download ``url`` into data_sources/, caching on disk. Returns text."""
    path = os.path.join(RAW, name)
    if os.path.exists(path) and os.path.getsize(path) > 0:
        print(f"  cached  {name}")
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    print(f"  fetch   {name}  <- {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "afriso-build"})
    with urllib.request.urlopen(req, timeout=120) as resp:  # noqa: S310
        text = resp.read().decode("utf-8")
    os.makedirs(RAW, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return text


def read_tab(text: str) -> list[dict]:
    return list(csv.DictReader(io.StringIO(text), delimiter="\t"))


def read_csv(text: str) -> list[dict]:
    return list(csv.DictReader(io.StringIO(text)))


def build():
    print("Downloading sources...")
    iso_rows = read_tab(fetch("iso-639-3.tab", SOURCES["iso-639-3.tab"]))
    name_rows = read_tab(
        fetch("iso-639-3_Name_Index.tab", SOURCES["iso-639-3_Name_Index.tab"])
    )
    glot_rows = read_csv(
        fetch("glottolog_languages.csv", SOURCES["glottolog_languages.csv"])
    )
    glot_name_rows = read_csv(
        fetch("glottolog_names.csv", SOURCES["glottolog_names.csv"])
    )
    macro_rows = read_tab(
        fetch(
            "iso-639-3-macrolanguages.tab",
            SOURCES["iso-639-3-macrolanguages.tab"],
        )
    )
    macro_members = defaultdict(list)  # M_Id -> [member I_Id, ...]
    for r in macro_rows:
        macro_members[r["M_Id"]].append(r["I_Id"])

    # --- Glottolog indexes -------------------------------------------------
    glot_by_iso = {}
    glot_name_by_code = {}
    for r in glot_rows:
        glot_name_by_code[r["Glottocode"]] = r["Name"]
        iso = r["ISO639P3code"].strip()
        if iso:
            glot_by_iso[iso] = r

    # --- SIL alternative names (keyed by ISO 639-3) ------------------------
    alt_by_code = defaultdict(set)
    for r in name_rows:
        code = r["Id"]
        for key in ("Print_Name", "Inverted_Name"):
            val = (r.get(key) or "").strip()
            if val:
                alt_by_code[code].add(val)

    # --- Glottolog alternative names (keyed by glottocode) -----------------
    # Keep endonyms / English / untagged names; drop localized translations
    # (lang tags like es/fr/zh) and descriptive "X language" forms.
    alt_by_glottocode = defaultdict(set)
    for r in glot_name_rows:
        if r.get("lang") not in ("", "en"):
            continue
        nm = (r.get("Name") or "").strip()
        low = nm.lower()
        if low in _NAME_JUNK or low.endswith(" language"):
            continue
        alt_by_glottocode[r["Language_ID"]].add(nm)

    africa2 = set(AFRICA)

    # -- Pass 1: Glottolog-derived enrichment for every ISO code -----------
    # Computed for ALL codes (not just African) so macrolanguages can
    # aggregate from their member individual languages.
    enrich = {}
    for r in iso_rows:
        code = r["Id"]
        ref_name = r["Ref_Name"].strip()
        glot = glot_by_iso.get(code)
        countries = macroareas = []
        family = family_glottocode = glottocode = None
        is_isolate = False
        latitude = longitude = None
        if glot:
            countries = [c for c in glot["Countries"].split(";") if c]
            macroareas = [m for m in glot["Macroarea"].split(";") if m]
            glottocode = glot["Glottocode"] or None
            is_isolate = glot.get("Is_Isolate") == "true"
            fam_id = glot["Family_ID"].strip()
            if fam_id:
                family_glottocode = fam_id
                family = glot_name_by_code.get(fam_id)
                if family == "Bookkeeping":  # Glottolog placeholder, not a family
                    family = family_glottocode = None
            elif is_isolate:
                family = f"{ref_name} (isolate)"
                family_glottocode = glottocode
            try:
                latitude = float(glot["Latitude"]) if glot["Latitude"] else None
                longitude = float(glot["Longitude"]) if glot["Longitude"] else None
            except ValueError:
                pass
        enrich[code] = {
            "ref_name": ref_name,
            "countries": countries,
            "macroareas": macroareas,
            "family": family,
            "family_glottocode": family_glottocode,
            "glottocode": glottocode,
            "is_isolate": is_isolate,
            "latitude": latitude,
            "longitude": longitude,
        }

    # -- Pass 2: assemble records, aggregating macrolanguages --------------
    languages = []
    for r in iso_rows:
        code = r["Id"]
        ref_name = r["Ref_Name"].strip()
        scope = r.get("Scope", "")
        e = enrich[code]
        countries = list(e["countries"])
        macroareas = list(e["macroareas"])
        family = e["family"]
        family_glottocode = e["family_glottocode"]

        # Alternative names: SIL name index + Glottolog name(s).
        alts = set(alt_by_code.get(code, set()))
        if e["glottocode"]:
            alts |= alt_by_glottocode.get(e["glottocode"], set())

        # Macrolanguage: aggregate coverage from member individual languages.
        if scope == "M":
            members = macro_members.get(code, [])
            member_countries, member_areas, member_families = set(), set(), Counter()
            for m in members:
                me = enrich.get(m)
                if not me:
                    continue
                member_countries.update(me["countries"])
                member_areas.update(me["macroareas"])
                if me["family"]:
                    member_families[me["family"]] += 1
                # a member's own name is a useful lookup alias for the macro
                alts.add(me["ref_name"])
            countries = sorted(set(countries) | member_countries)
            macroareas = sorted(set(macroareas) | member_areas)
            if not family and member_families:
                family, _ = member_families.most_common(1)[0]
                family_glottocode = None

        african_countries = sorted(c for c in countries if c in africa2)
        in_africa = bool(african_countries) or ("Africa" in macroareas)
        if not in_africa:
            continue

        seen = {ref_name.lower()}
        alt_names = []
        for nm in sorted(alts, key=str.lower):
            if nm.lower() not in seen:
                seen.add(nm.lower())
                alt_names.append(nm)

        languages.append(
            {
                "iso639_3": code,
                "name": ref_name,
                "alt_names": alt_names,
                "iso639_1": (r.get("Part1") or "").strip() or None,
                "iso639_2b": (r.get("Part2b") or "").strip() or None,
                "iso639_2t": (r.get("Part2t") or "").strip() or None,
                "scope": SCOPE_LABELS.get(scope, scope),
                "type": TYPE_LABELS.get(
                    r.get("Language_Type", ""), r.get("Language_Type")
                ),
                "glottocode": e["glottocode"],
                "family": family,
                "family_glottocode": family_glottocode,
                "is_isolate": e["is_isolate"],
                "countries": african_countries,
                "regions": sorted({AFRICA[c][2] for c in african_countries}),
                "macroareas": macroareas,
                "latitude": e["latitude"],
                "longitude": e["longitude"],
            }
        )

    # -- Pass 3: propagate countries from macrolanguages to their members ---
    # Glottolog sometimes records a country only at the macrolanguage level
    # (e.g. Akan) leaving individual members (Twi, Fanti) with none.
    member_to_macro = {}
    for m_id, members in macro_members.items():
        for i_id in members:
            member_to_macro[i_id] = m_id
    macro_countries = {
        lang["iso639_3"]: lang["countries"]
        for lang in languages
        if lang["scope"] == "macrolanguage"
    }
    for lang in languages:
        if lang["countries"]:
            continue
        parent = member_to_macro.get(lang["iso639_3"])
        inherited = macro_countries.get(parent) if parent else None
        if inherited:
            lang["countries"] = list(inherited)
            lang["regions"] = sorted({AFRICA[c][2] for c in inherited})

    languages.sort(key=lambda x: x["name"].lower())

    # --- Country table -----------------------------------------------------
    lang_count = defaultdict(int)
    for lang in languages:
        for c in lang["countries"]:
            lang_count[c] += 1
    countries_out = []
    for code2, (code3, name, region) in sorted(
        AFRICA.items(), key=lambda kv: kv[1][1]
    ):
        countries_out.append(
            {
                "code2": code2,
                "code3": code3,
                "name": name,
                "region": region,
                "language_count": lang_count.get(code2, 0),
            }
        )

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "languages.json"), "w", encoding="utf-8") as fh:
        json.dump(languages, fh, ensure_ascii=False, separators=(",", ":"))
    with open(os.path.join(OUT, "countries.json"), "w", encoding="utf-8") as fh:
        json.dump(countries_out, fh, ensure_ascii=False, indent=2)
    with open(os.path.join(OUT, "meta.json"), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "language_count": len(languages),
                "country_count": len(countries_out),
                "sources": {
                    "iso639_3": "SIL ISO 639-3 code tables (iso639-3.sil.org)",
                    "glottolog": f"Glottolog {GLOTTOLOG_VERSION} (CC-BY 4.0)",
                },
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )

    # --- Summary -----------------------------------------------------------
    fams = defaultdict(int)
    for lang in languages:
        fams[lang["family"] or "(unclassified)"] += 1
    with_glot = sum(1 for x in languages if x["glottocode"])
    with_alts = sum(1 for x in languages if x["alt_names"])
    print(f"\nBuilt {len(languages)} African languages across {len(countries_out)} countries.")
    print(f"  with glottocode/family: {with_glot}   with alt names: {with_alts}")
    print(f"  families: {len(fams)}")
    for fam, n in sorted(fams.items(), key=lambda kv: -kv[1])[:10]:
        print(f"    {n:5d}  {fam}")
    print(f"\nWrote -> {OUT}")


if __name__ == "__main__":
    build()
