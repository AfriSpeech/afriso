#!/usr/bin/env python3
"""Seed and refresh the afriso dataset from open sources.

The dataset (``src/afriso/data/languages.csv``) is the source of truth and is
curated by hand via pull requests. This script is **additive and
non-destructive**:

* First run (no CSV yet): writes the full seed from SIL ISO 639-3 + Glottolog.
* Later runs: only **adds** languages that are newly published upstream and are
  not already in the CSV. Existing rows are **never modified**, so human
  corrections always win.

``countries.csv`` is regenerated from ``africa_countries.py`` each run (it is
not hand-curated as language data).

Sources
-------
* SIL ISO 639-3 code tables (public).
* Glottolog v5.2 (CC-BY 4.0), via the glottolog-cldf release.

Run:  python scripts/seed_data.py            # seed or additive refresh
      python scripts/seed_data.py --dry-run  # show what would be added
"""
from __future__ import annotations

import argparse
import csv
import io
import os
import sys
import urllib.request
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW = os.path.join(ROOT, "data_sources")
OUT = os.path.join(ROOT, "src", "afriso", "data")

sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))
from africa_countries import AFRICA  # noqa: E402
from afriso._schema import (  # noqa: E402
    COUNTRY_COLUMNS,
    LANGUAGE_COLUMNS,
    language_to_row,
)

GLOTTOLOG_VERSION = "v5.2"
SIL_BASE = "https://iso639-3.sil.org/sites/iso639-3/files/downloads"
GLOT_BASE = (
    "https://raw.githubusercontent.com/glottolog/glottolog-cldf/"
    f"{GLOTTOLOG_VERSION}/cldf"
)
SOURCES = {
    "iso-639-3.tab": f"{SIL_BASE}/iso-639-3.tab",
    "iso-639-3_Name_Index.tab": f"{SIL_BASE}/iso-639-3_Name_Index.tab",
    "iso-639-3-macrolanguages.tab": f"{SIL_BASE}/iso-639-3-macrolanguages.tab",
    "glottolog_languages.csv": f"{GLOT_BASE}/languages.csv",
    "glottolog_names.csv": f"{GLOT_BASE}/names.csv",
}

SCOPE_LABELS = {"I": "individual", "M": "macrolanguage", "S": "special"}
TYPE_LABELS = {
    "L": "living", "E": "extinct", "A": "ancient",
    "H": "historical", "C": "constructed", "S": "special",
}
_NAME_JUNK = {"not specified", "unnamed", "undetermined", "unknown", ""}


def fetch(name: str, url: str) -> str:
    path = os.path.join(RAW, name)
    if os.path.exists(path) and os.path.getsize(path) > 0:
        print(f"  cached  {name}")
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    print(f"  fetch   {name}")
    req = urllib.request.Request(url, headers={"User-Agent": "afriso-seed"})
    with urllib.request.urlopen(req, timeout=120) as resp:  # noqa: S310
        text = resp.read().decode("utf-8")
    os.makedirs(RAW, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return text


def _tab(text):
    return list(csv.DictReader(io.StringIO(text), delimiter="\t"))


def _csv(text):
    return list(csv.DictReader(io.StringIO(text)))


def generate() -> list[dict]:
    """Build the full African language table from upstream sources."""
    print("Downloading sources...")
    iso_rows = _tab(fetch("iso-639-3.tab", SOURCES["iso-639-3.tab"]))
    name_rows = _tab(fetch("iso-639-3_Name_Index.tab", SOURCES["iso-639-3_Name_Index.tab"]))
    macro_rows = _tab(fetch("iso-639-3-macrolanguages.tab", SOURCES["iso-639-3-macrolanguages.tab"]))
    glot_rows = _csv(fetch("glottolog_languages.csv", SOURCES["glottolog_languages.csv"]))
    glot_name_rows = _csv(fetch("glottolog_names.csv", SOURCES["glottolog_names.csv"]))

    glot_by_iso, glot_name_by_code = {}, {}
    for r in glot_rows:
        glot_name_by_code[r["Glottocode"]] = r["Name"]
        if r["ISO639P3code"].strip():
            glot_by_iso[r["ISO639P3code"].strip()] = r

    macro_members = defaultdict(list)
    for r in macro_rows:
        macro_members[r["M_Id"]].append(r["I_Id"])

    alt_by_code = defaultdict(set)
    for r in name_rows:
        for key in ("Print_Name", "Inverted_Name"):
            v = (r.get(key) or "").strip()
            if v:
                alt_by_code[r["Id"]].add(v)

    alt_by_glottocode = defaultdict(set)
    for r in glot_name_rows:
        if r.get("lang") not in ("", "en"):
            continue
        nm = (r.get("Name") or "").strip()
        if nm.lower() in _NAME_JUNK or nm.lower().endswith(" language"):
            continue
        alt_by_glottocode[r["Language_ID"]].add(nm)

    africa2 = set(AFRICA)

    # Pass 1: Glottolog enrichment for every ISO code.
    enrich = {}
    for r in iso_rows:
        code, ref_name = r["Id"], r["Ref_Name"].strip()
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
                if family == "Bookkeeping":
                    family = family_glottocode = None
            elif is_isolate:
                family = f"{ref_name} (isolate)"
                family_glottocode = glottocode
            try:
                latitude = float(glot["Latitude"]) if glot["Latitude"] else None
                longitude = float(glot["Longitude"]) if glot["Longitude"] else None
            except ValueError:
                pass
        enrich[code] = dict(
            ref_name=ref_name, countries=countries, macroareas=macroareas,
            family=family, family_glottocode=family_glottocode,
            glottocode=glottocode, is_isolate=is_isolate,
            latitude=latitude, longitude=longitude,
        )

    # Pass 2: assemble records, aggregating macrolanguages.
    languages = []
    for r in iso_rows:
        code, ref_name, scope = r["Id"], r["Ref_Name"].strip(), r.get("Scope", "")
        e = enrich[code]
        countries, macroareas = list(e["countries"]), list(e["macroareas"])
        family, family_glottocode = e["family"], e["family_glottocode"]
        alts = set(alt_by_code.get(code, set()))
        if e["glottocode"]:
            alts |= alt_by_glottocode.get(e["glottocode"], set())

        if scope == "M":
            member_countries, member_areas, member_families = set(), set(), Counter()
            for m in macro_members.get(code, []):
                me = enrich.get(m)
                if not me:
                    continue
                member_countries.update(me["countries"])
                member_areas.update(me["macroareas"])
                if me["family"]:
                    member_families[me["family"]] += 1
                alts.add(me["ref_name"])
            countries = sorted(set(countries) | member_countries)
            macroareas = sorted(set(macroareas) | member_areas)
            if not family and member_families:
                family = member_families.most_common(1)[0][0]
                family_glottocode = None

        african = sorted(c for c in countries if c in africa2)
        if not african and "Africa" not in macroareas:
            continue

        seen = {ref_name.lower()}
        alt_names = []
        for nm in sorted(alts, key=str.lower):
            if nm.lower() not in seen:
                seen.add(nm.lower())
                alt_names.append(nm)

        languages.append({
            "iso639_3": code, "name": ref_name, "alt_names": alt_names,
            "iso639_1": (r.get("Part1") or "").strip() or None,
            "iso639_2b": (r.get("Part2b") or "").strip() or None,
            "iso639_2t": (r.get("Part2t") or "").strip() or None,
            "scope": SCOPE_LABELS.get(scope, scope),
            "type": TYPE_LABELS.get(r.get("Language_Type", ""), r.get("Language_Type")),
            "glottocode": e["glottocode"], "family": family,
            "family_glottocode": family_glottocode, "is_isolate": e["is_isolate"],
            "countries": african, "latitude": e["latitude"], "longitude": e["longitude"],
        })

    # Pass 3: propagate countries from macrolanguages to their members.
    member_to_macro = {i: m for m, ms in macro_members.items() for i in ms}
    macro_countries = {x["iso639_3"]: x["countries"] for x in languages if x["scope"] == "macrolanguage"}
    for x in languages:
        if not x["countries"]:
            parent = member_to_macro.get(x["iso639_3"])
            if parent and macro_countries.get(parent):
                x["countries"] = list(macro_countries[parent])

    return languages


def load_existing_codes(path: str):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8", newline="") as fh:
        return {row["iso639_3"] for row in csv.DictReader(fh)}


def write_languages(path: str, generated: list[dict]):
    """Additive merge: keep existing rows verbatim, append new upstream codes."""
    existing_codes = load_existing_codes(path)
    existing_rows = []
    if existing_codes is not None:
        with open(path, encoding="utf-8", newline="") as fh:
            existing_rows = list(csv.DictReader(fh))

    new = [g for g in generated if existing_codes is None or g["iso639_3"] not in existing_codes]
    rows = existing_rows + [language_to_row(g) for g in new]
    rows.sort(key=lambda r: (r["name"].lower(), r["iso639_3"]))

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=LANGUAGE_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return existing_codes, new, len(rows)


def write_countries(path: str):
    rows = [
        {"code2": c2, "code3": c3, "name": nm, "region": rg}
        for c2, (c3, nm, rg) in sorted(AFRICA.items(), key=lambda kv: kv[1][1])
    ]
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=COUNTRY_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def main():
    ap = argparse.ArgumentParser(description="Seed / additively refresh the afriso dataset.")
    ap.add_argument("--dry-run", action="store_true", help="report additions without writing")
    args = ap.parse_args()

    generated = generate()
    lang_path = os.path.join(OUT, "languages.csv")
    existing_codes = load_existing_codes(lang_path)

    if args.dry_run:
        if existing_codes is None:
            print(f"\n[dry-run] would seed {len(generated)} languages (no CSV yet).")
        else:
            new = [g for g in generated if g["iso639_3"] not in existing_codes]
            print(f"\n[dry-run] {len(new)} new upstream languages would be added:")
            for g in new[:50]:
                print(f"    + {g['iso639_3']}  {g['name']}")
            if len(new) > 50:
                print(f"    ... and {len(new) - 50} more")
        return

    prev, new, total = write_languages(lang_path, generated)
    ncountries = write_countries(os.path.join(OUT, "countries.csv"))

    if prev is None:
        print(f"\nSeeded {total} languages, {ncountries} countries -> {OUT}")
    else:
        print(f"\nAdded {len(new)} new languages (existing {len(prev)} rows untouched).")
        for g in new[:30]:
            print(f"    + {g['iso639_3']}  {g['name']}")
        print(f"Total {total} languages, {ncountries} countries -> {OUT}")


if __name__ == "__main__":
    main()
