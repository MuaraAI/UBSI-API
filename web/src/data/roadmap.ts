import { RoadmapItem } from "@/types";

export const ROADMAP_ITEMS: RoadmapItem[] = [
  {
    version: "v1.2",
    title: "Auto-Attendance & Presensi Kuliah",
    description:
      "Operasi write otomatisasi presensi MyBest berbasis jadwal harian dengan proteksi human-jitter dan toggle On/Off via API.",
    badge: "Write Automation",
    status: "upcoming",
  },
  {
    version: "v1.2",
    title: "Ekspor Kalender iCal (.ics)",
    description:
      "Sinkronisasi otomatis jadwal kuliah SIAKAD langsung ke Google Calendar di Android dan Apple Calendar di iOS.",
    badge: "Calendar Sync",
    status: "upcoming",
  },
  {
    version: "v1.2",
    title: "Rekap Nilai Tugas & Kuis Elearning",
    description:
      "Tracking status pengumpulan dan rekapitulasi nilai tugas 6 mata kuliah aktif per setiap pertemuan secara terstruktur.",
    badge: "Elearning Grades",
    status: "upcoming",
  },
  {
    version: "v1.2",
    title: "Bulk Modul Downloader",
    description:
      "Unduh seluruh berkas materi perkuliahan, slide presentasi, dan silabus 6 matkul sekaligus dalam satu file terkompresi.",
    badge: "Automation",
    status: "planned",
  },
  {
    version: "v1.2",
    title: "Kalkulator & Simulator IPK",
    description:
      "Simulasi perhitungan Indeks Prestasi Kumulatif berdasarkan riwayat nilai murni dan estimasi bobot nilai semester berjalan.",
    badge: "Productivity",
    status: "planned",
  },
];
