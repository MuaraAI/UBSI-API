from pathlib import Path

from app.modules.elearning import summarize_grades

FIXTURES = Path(__file__).parent / "fixtures"

SUBS = [
    {"id": "a1", "kode": "121-PBO", "judul": "T1", "pertemuan": "Pertemuan 3", "nilai": 90.0},
    {"id": "a2", "kode": "121-PBO", "judul": "T2", "pertemuan": "Pertemuan 4", "nilai": 85.0},
    {"id": "a3", "kode": "131-BASDAT", "judul": "T3", "pertemuan": "Pertemuan 2", "nilai": 78.0},
    {"id": "a4", "kode": "131-BASDAT", "judul": "T4", "pertemuan": "Pertemuan 5", "nilai": None},
]

QUIZZES = [
    {
        "id": "q1",
        "kode_mtk": None,
        "paket": "LATIHAN",
        "dosen": "NPR",
        "waktu": "30menit",
        "ujian_mulai": "2026-09-25 10:35:00",
        "ujian_selesai": "2026-09-25 11:05:00",
    }
]

def test_summarize_totals():
    recap = summarize_grades(SUBS, QUIZZES)
    assert recap["total_tugas"] == 4
    assert recap["sudah_dinilai"] == 3
    assert recap["belum_dinilai"] == 1
    assert recap["rata_nilai"] == round((90 + 85 + 78) / 3, 2)
    assert recap["nilai_max"] == 90.0
    assert recap["nilai_min"] == 78.0

def test_summarize_per_pertemuan_sorted():
    recap = summarize_grades(SUBS, QUIZZES)
    rows = recap["per_pertemuan"]
    assert [r["pertemuan"] for r in rows] == [
        "Pertemuan 2",
        "Pertemuan 3",
        "Pertemuan 4",
        "Pertemuan 5",
    ]

    p5 = rows[-1]
    assert p5["total_tugas"] == 1
    assert p5["sudah_dinilai"] == 0
    assert p5["belum_dinilai"] == 1
    assert p5["rata_nilai"] is None
    assert p5["nilai_max"] is None

def test_summarize_per_matkul():
    recap = summarize_grades(SUBS, QUIZZES)
    per_matkul = recap["per_matkul"]
    assert set(per_matkul.keys()) == {"121-PBO", "131-BASDAT"}
    assert per_matkul["121-PBO"]["total_tugas"] == 2
    assert per_matkul["121-PBO"]["rata_nilai"] == 87.5
    assert per_matkul["131-BASDAT"]["total_tugas"] == 1

def test_summarize_quiz_section():
    recap = summarize_grades(SUBS, QUIZZES)
    assert recap["kuis"] == [
        {
            "paket": "LATIHAN",
            "kode_mtk": None,
            "dosen": "NPR",
            "ujian_mulai": "2026-09-25 10:35:00",
            "ujian_selesai": "2026-09-25 11:05:00",
        }
    ]

def test_summarize_empty():
    recap = summarize_grades([], [])
    assert recap["total_tugas"] == 0
    assert recap["sudah_dinilai"] == 0
    assert recap["rata_nilai"] is None
    assert recap["per_pertemuan"] == []
    assert recap["per_matkul"] == {}
    assert recap["kuis"] == []

def test_summarize_from_fixture():
    from app.modules.elearning import parse_assignments

    html = (FIXTURES / "el_assignment_grades.html").read_text(encoding="utf-8")
    subs = parse_assignments(html)["submissions"]
    recap = summarize_grades(subs, [])
    assert recap["total_tugas"] == 3
    assert recap["sudah_dinilai"] == 3
    assert recap["nilai_max"] == 90.0
    assert recap["nilai_min"] == 78.0
    assert recap["per_matkul"]["121-PBO"]["rata_nilai"] == 87.5
    assert recap["per_matkul"]["131-BASDAT"]["rata_nilai"] == 78.0
    assert [r["pertemuan"] for r in recap["per_pertemuan"]] == [
        "Pertemuan 2",
        "Pertemuan 3",
        "Pertemuan 4",
    ]
