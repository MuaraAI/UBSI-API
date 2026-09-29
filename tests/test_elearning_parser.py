from pathlib import Path
import pytest
from app.modules.elearning import (
    solve_captcha,
    parse_courses,
    parse_assignments,
    parse_presence,
    parse_materials,
    parse_quiz,
)

FIXTURES = Path(__file__).parent / "fixtures"

def test_solve_captcha():
    # Legacy math captcha
    assert solve_captcha("Berapa hasil dari 4 + 3?") == 7
    assert solve_captcha("Berapa hasil dari 1 + 5?") == 6
    assert solve_captcha("12 + 15") == 27
    assert solve_captcha("Berapa hasil dari 10 + 0?") == 10

    # New SVG text captcha
    svg_sample = "<svg><text x='30'>4</text><text x='68'>E</text><text x='101'>7</text></svg>"
    assert solve_captcha(svg_sample) == "4E7"

def test_parse_courses():
    html = (FIXTURES / "el_sch.html").read_text(encoding="utf-8")
    courses = parse_courses(html)
    assert len(courses) == 6
    first = courses[0]
    assert first["kode"] != ""
    assert first["nama"] != ""
    assert isinstance(first["sks"], int)
    assert first["hari"] != ""
    assert first["jam"] != ""
    assert first["token_absen"] is not None
    assert first["token_assignment"] is not None
    assert first["token_learning"] is not None

def test_parse_assignments():
    html = (FIXTURES / "el_assignment_1.html").read_text(encoding="utf-8")
    data = parse_assignments(html)
    assert "tasks" in data
    assert "submissions" in data
    assert isinstance(data["tasks"], list)
    assert isinstance(data["submissions"], list)

def test_parse_assignments_grades_rows():
    html = (FIXTURES / "el_assignment_grades.html").read_text(encoding="utf-8")
    data = parse_assignments(html)
    subs = data["submissions"]
    assert len(subs) == 3

    first = subs[0]
    assert first["kode"] == "121-PBO"
    assert first["judul"] == "Implementasi Class"
    assert first["pertemuan"] == "Pertemuan 3"
    assert first["nilai"] == 90.0
    assert first["link_tugas"].startswith("https://elearning.bsi.ac.id/")

    graded = [s for s in subs if s["nilai"] is not None]
    assert len(graded) == 3

def test_parse_presence():
    html = (FIXTURES / "el_absen_1.html").read_text(encoding="utf-8")
    presence = parse_presence(html)
    assert isinstance(presence, list)

def test_parse_materials():
    html = (FIXTURES / "el_learning_1.html").read_text(encoding="utf-8")
    materials = parse_materials(html)
    assert isinstance(materials, list)
    assert len(materials) >= 1
    assert materials[0]["file_url"] != ""

def test_parse_quiz():
    html = (FIXTURES / "el_exercise.html").read_text(encoding="utf-8")
    quizzes = parse_quiz(html)
    assert isinstance(quizzes, list)
