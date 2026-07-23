"""Tests for the afriso command-line interface."""
import json

import pytest

from afriso.cli import main


def test_cli_iso(capsys):
    assert main(["iso", "Yoruba"]) == 0
    assert capsys.readouterr().out.strip() == "yor"


def test_cli_name(capsys):
    assert main(["name", "hau"]) == 0
    assert capsys.readouterr().out.strip() == "Hausa"


def test_cli_iso_unknown_exits_nonzero(capsys):
    assert main(["iso", "Klingon"]) == 1


def test_cli_get_json(capsys):
    assert main(["get", "bam"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["iso639_3"] == "bam"


def test_cli_country_codes(capsys):
    assert main(["country", "Ghana", "--format", "codes"]) == 0
    codes = capsys.readouterr().out.split()
    assert "twi" in codes


def test_cli_region_family_filter(capsys):
    assert main(["region", "West Africa", "--family", "Mande", "--format", "codes"]) == 0
    codes = capsys.readouterr().out.split()
    assert "bam" in codes


def test_cli_bad_region_exits_2(capsys):
    assert main(["region", "Atlantis"]) == 2


def test_cli_families(capsys):
    assert main(["families"]) == 0
    assert "Atlantic-Congo" in capsys.readouterr().out
