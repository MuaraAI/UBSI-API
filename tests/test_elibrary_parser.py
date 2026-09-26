from pathlib import Path
import pytest
from app.modules.elibrary import parse_opac_search, parse_book_detail

FIXTURES = Path(__file__).parent / "fixtures"

def test_parse_opac_search():
    html = (FIXTURES / "el_search_ok.html").read_text(encoding="utf-8")
    data = parse_opac_search(html)
    assert data["total_count"] == 967
    assert len(data["items"]) >= 10
    first = data["items"][0]
    assert first["title"] != ""
    assert "readbook" in first["url"]
    assert first["id"] != ""

def test_parse_book_detail():
    html = (FIXTURES / "el_book_detail.html").read_text(encoding="utf-8")
    data = parse_book_detail(html)
    assert data["kode_buku"] == "206060"
    assert "Metode penelitian" in data["judul_buku"]
    assert data["penulis"] == "Sugiyono"
    assert data["penerbit"] == "ALFABETA"
    assert data["tahun"] == 2017
    assert data["stok"] == 3
    assert data["eksemplar"] == 3
    assert data["isbn"] == "979-8433-64-0"
