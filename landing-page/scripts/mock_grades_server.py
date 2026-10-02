"""Mock /v1/elearning/grades server untuk verifikasi visual UI /recap.

Pemakaian: python mock_grades_server.py [port]   (default 8399)
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

SAMPLE = {
    "success": True,
    "cached": False,
    "data": {
        "total_tugas": 18,
        "sudah_dinilai": 14,
        "belum_dinilai": 4,
        "rata_nilai": 86.43,
        "nilai_max": 100.0,
        "nilai_min": 70.0,
        "per_matkul": {
            "101": {"total_tugas": 4, "rata_nilai": 88.75},
            "104": {"total_tugas": 4, "rata_nilai": 85.0},
            "153": {"total_tugas": 3, "rata_nilai": 90.33},
            "205": {"total_tugas": 4, "rata_nilai": 82.5},
            "217": {"total_tugas": 3, "rata_nilai": 87.0},
        },
        "per_pertemuan": [
            {"pertemuan": "Pertemuan 1", "total_tugas": 5, "sudah_dinilai": 5,
             "belum_dinilai": 0, "rata_nilai": 88.4, "nilai_max": 95.0, "nilai_min": 80.0,
             "items": []},
            {"pertemuan": "Pertemuan 2", "total_tugas": 5, "sudah_dinilai": 4,
             "belum_dinilai": 1, "rata_nilai": 85.25, "nilai_max": 100.0, "nilai_min": 70.0,
             "items": []},
            {"pertemuan": "Pertemuan 3", "total_tugas": 4, "sudah_dinilai": 3,
             "belum_dinilai": 1, "rata_nilai": 86.67, "nilai_max": 92.0, "nilai_min": 78.0,
             "items": []},
            {"pertemuan": "Pertemuan 4", "total_tugas": 4, "sudah_dinilai": 2,
             "belum_dinilai": 2, "rata_nilai": 84.5, "nilai_max": 89.0, "nilai_min": 80.0,
             "items": []},
        ],
        "kuis": [
            {"paket": "Paket 1", "kode_mtk": "101", "dosen": "Dr. Ir. Hendra S., M.Kom",
             "ujian_mulai": "2026-09-28 08:00", "ujian_selesai": "2026-09-28 10:30"},
            {"paket": "Paket 2", "kode_mtk": "104", "dosen": "Ahmad Fauzi, M.Kom",
             "ujian_mulai": "2026-09-30 13:00", "ujian_selesai": "2026-09-30 15:00"},
        ],
    },
}

ITEMS = {
    "success": True,
    "cached": True,
    "data": {
        "total_tugas": 18,
        "sudah_dinilai": 14,
        "belum_dinilai": 4,
        "rata_nilai": 86.43,
        "nilai_max": 100.0,
        "nilai_min": 70.0,
        "per_matkul": SAMPLE["data"]["per_matkul"],
        "per_pertemuan": [
            {"pertemuan": "Pertemuan 1", "total_tugas": 5, "sudah_dinilai": 5,
             "belum_dinilai": 0, "rata_nilai": 88.4, "nilai_max": 95.0, "nilai_min": 80.0,
             "items": [
                 {"id": "a1", "kode": "101", "judul": "Tugas 1 - Analisis Pasar",
                  "pertemuan": "Pertemuan 1", "komentar_dosen": "Bagus, tambahkan referensi",
                  "nilai": 90.0, "mata_kuliah": "Dasar Manajemen Bisnis"},
                 {"id": "a2", "kode": "104", "judul": "Tugas 1 - Flowchart Algoritma",
                  "pertemuan": "Pertemuan 1", "komentar_dosen": None,
                  "nilai": 85.0, "mata_kuliah": "Logika & Algoritma"},
             ]},
            {"pertemuan": "Pertemuan 2", "total_tugas": 5, "sudah_dinilai": 4,
             "belum_dinilai": 1, "rata_nilai": 85.25, "nilai_max": 100.0, "nilai_min": 70.0,
             "items": [
                 {"id": "a3", "kode": "153", "judul": "Tugas 2 - Sejarah Komputer",
                  "pertemuan": "Pertemuan 2", "komentar_dosen": "Perdalam bab 3",
                  "nilai": 78.0, "mata_kuliah": "Pengantar Teknologi Informasi"},
                 {"id": "a4", "kode": "205", "judul": "Tugas 2 - Basis Data Relasional",
                  "pertemuan": "Pertemuan 2", "komentar_dosen": None,
                  "nilai": None, "mata_kuliah": "Sistem Basis Data"},
             ]},
        ],
        "kuis": SAMPLE["data"]["kuis"],
    },
}


class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "X-API-Key, Accept")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_GET(self):
        body = ITEMS if "grades" in self.path else SAMPLE
        payload = json.dumps(body).encode()
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        pass


HTTPServer(("127.0.0.1", int(sys.argv[1]) if len(sys.argv) > 1 else 8399), Handler).serve_forever()
