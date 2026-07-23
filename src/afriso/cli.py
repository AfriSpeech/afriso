"""Command-line interface for afriso.

Examples
--------
    afriso iso Yoruba
    afriso name hau
    afriso country Nigeria --format csv > ng.csv
    afriso region "West Africa" --family Mande --format json
    afriso family Atlantic-Congo --format table
    afriso families
    afriso search swahili
"""
from __future__ import annotations

import argparse
import json
import sys

from . import core
from .models import LanguageSet


def _emit(langs: LanguageSet, fmt: str) -> None:
    if fmt == "json":
        print(langs.to_json())
    elif fmt == "csv":
        sys.stdout.write(langs.to_csv())
    elif fmt == "codes":
        print("\n".join(langs.codes()))
    else:  # table
        for x in langs.sorted_by("name"):
            fam = x.family or "-"
            print(f"{x.iso639_3}\t{x.name}\t{fam}\t{','.join(x.countries)}")


def _add_format(p, default="table"):
    p.add_argument(
        "--format", "-f",
        choices=["table", "csv", "json", "codes"],
        default=default,
        help="output format (default: %(default)s)",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="afriso",
        description="Map African language names to ISO 639-3 codes, countries and families.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("iso", help="print the ISO 639-3 code for a language name")
    p.add_argument("name")

    p = sub.add_parser("name", help="print the language name for a code")
    p.add_argument("code")

    p = sub.add_parser("get", help="print all fields for a language (JSON)")
    p.add_argument("key")

    p = sub.add_parser("search", help="substring search over names and alt names")
    p.add_argument("query")
    _add_format(p)

    for name, help_ in [
        ("country", "list languages of a country (code or name)"),
        ("region", "list languages of a region"),
        ("family", "list languages of a family"),
    ]:
        p = sub.add_parser(name, help=help_)
        p.add_argument("value")
        p.add_argument("--family", help="further filter by family (country/region only)")
        _add_format(p)

    sub.add_parser("families", help="list language families with counts")
    sub.add_parser("regions", help="list regions")
    p = sub.add_parser("countries", help="list African countries")
    p.add_argument("--region", help="filter by region")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    cmd = args.command

    try:
        if cmd == "iso":
            code = core.to_iso(args.name)
            if not code:
                print(f"No match for {args.name!r}", file=sys.stderr)
                return 1
            print(code)
        elif cmd == "name":
            nm = core.to_name(args.code)
            if not nm:
                print(f"No match for {args.code!r}", file=sys.stderr)
                return 1
            print(nm)
        elif cmd == "get":
            lang = core.get(args.key)
            if not lang:
                print(f"No match for {args.key!r}", file=sys.stderr)
                return 1
            print(json.dumps(lang.to_dict(), ensure_ascii=False, indent=2))
        elif cmd == "search":
            _emit(core.search(args.query), args.format)
        elif cmd in ("country", "region", "family"):
            fn = {"country": core.by_country, "region": core.by_region, "family": core.by_family}[cmd]
            langs = fn(args.value)
            if cmd in ("country", "region") and args.family:
                langs = langs.by_family(args.family)
            _emit(langs, args.format)
        elif cmd == "families":
            for fam, n in core.families(with_counts=True):
                print(f"{n:5d}  {fam}")
        elif cmd == "regions":
            print("\n".join(core.regions()))
        elif cmd == "countries":
            for c in core.countries(region=getattr(args, "region", None)):
                print(f"{c.code2}\t{c.code3}\t{c.name}\t{c.region}\t{c.language_count}")
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
