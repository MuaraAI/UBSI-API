from pathlib import Path
from app.modules.studentv2 import (
    parse_schedule,
    parse_grades,
    parse_news,
    parse_announcements,
)

FIXTURES = Path(__file__).parent / "fixtures"

def test_parse_schedule():
    html = (FIXTURES / "sv2_jadwal.html").read_text(encoding="utf-8")
    courses = parse_schedule(html)
    assert len(courses) == 6
    first = courses[0]
    assert first["kode"] != ""
    assert first["nama"] != ""
    assert first["hari"] != ""
    assert first["jam"] != ""
    assert isinstance(first["sks"], int)
    assert first["ruang"] != ""
    assert first["id"] != ""

def test_parse_grades():
    html = (FIXTURES / "sv2_nilai_murni.html").read_text(encoding="utf-8")
    grades = parse_grades(html)
    assert len(grades) == 6
    first = grades[0]
    assert first["kode"] != ""
    assert first["nama"] != ""
    assert isinstance(first["sks"], int)
    assert "total" in first
    assert "grade" in first
    assert first["id"] != ""

def test_parse_news():
    html = (FIXTURES / "sv2_berita.html").read_text(encoding="utf-8")
    news = parse_news(html)
    assert len(news) > 50
    first = news[0]
    assert first["title"] != ""
    assert first["pdf_url"].startswith("http")
    assert first["date"] != ""
    assert first["id"] != ""

def test_parse_announcements():
    html = (FIXTURES / "sv2_beranda.html").read_text(encoding="utf-8")
    items = parse_announcements(html)
    assert len(items) >= 1
    first = items[0]
    assert first["title"] != ""
    assert first["pdf_url"].startswith("http")
    assert first["id"] != ""
