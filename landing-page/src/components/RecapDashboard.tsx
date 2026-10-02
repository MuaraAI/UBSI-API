"use client";

import React, { useMemo, useState } from "react";

type SubmissionItem = {
  id: string;
  kode: string;
  judul: string;
  pertemuan: string;
  link_tugas?: string;
  komentar_dosen: string | null;
  nilai: number | null;
  mata_kuliah?: string;
};

type PertemuanRow = {
  pertemuan: string;
  total_tugas: number;
  sudah_dinilai: number;
  belum_dinilai: number;
  rata_nilai: number | null;
  nilai_max: number | null;
  nilai_min: number | null;
  items: SubmissionItem[];
};

type QuizRow = {
  paket: string | null;
  kode_mtk: string | null;
  dosen: string | null;
  ujian_mulai: string | null;
  ujian_selesai: string | null;
};

type GradesData = {
  total_tugas: number;
  sudah_dinilai: number;
  belum_dinilai: number;
  rata_nilai: number | null;
  nilai_max: number | null;
  nilai_min: number | null;
  per_matkul: Record<string, { total_tugas: number; rata_nilai: number }>;
  per_pertemuan: PertemuanRow[];
  kuis: QuizRow[];
};

function fmt(value: number | null | undefined): string {
  if (value === null || value === undefined) return "—";
  return Number.isInteger(value) ? String(value) : value.toFixed(2);
}

const thClass =
  "px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-[0.12em] text-secondary whitespace-nowrap";

const tdClass = "px-5 py-3 whitespace-nowrap";

export function RecapDashboard() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<{ title: string; hint: string } | null>(null);
  const [data, setData] = useState<GradesData | null>(null);
  const [backend, setBackend] = useState<string | null>(null);
  const [meta, setMeta] = useState<{
    cached: boolean;
    stale: boolean;
    fetchedAt: string;
  } | null>(null);

  const load = async () => {
    if (loading) return;

    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/recap", { cache: "no-store" });
      const body = (await res.json()) as {
        success?: boolean;
        data?: GradesData;
        cached?: boolean;
        stale?: boolean;
        backend?: string;
        error?: { code?: string; message?: string; hint?: string };
      };

      setBackend(body.backend ?? null);

      if (!res.ok || !body.success) {
        setError({
          title: body.error?.message ?? `Server merespons ${res.status}`,
          hint:
            body.error?.hint ??
            "Periksa log server web dan backend untuk detail kesalahan.",
        });
        return;
      }

      setData(body.data ?? null);
      setMeta({
        cached: Boolean(body.cached),
        stale: Boolean(body.stale),
        fetchedAt: new Date().toLocaleTimeString("id-ID"),
      });
    } catch {
      setError({
        title: "Gagal memuat rekap",
        hint: "Server web tidak merespons dengan benar. Muat ulang halaman lalu coba lagi.",
      });
    } finally {
      setLoading(false);
    }
  };

  const submissions = useMemo(
    () => (data ? data.per_pertemuan.flatMap((p) => p.items) : []),
    [data]
  );

  const courseNames = useMemo(() => {
    const map: Record<string, string> = {};
    for (const s of submissions) {
      if (s.kode && s.mata_kuliah && !map[s.kode]) map[s.kode] = s.mata_kuliah;
    }
    return map;
  }, [submissions]);

  const hasData = data !== null;

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 py-14 sm:py-20">
      {/* Header */}
      <p className="section-kicker mb-3">MyBest Elearning · v1.2</p>
      <h1 className="font-display text-3xl sm:text-4xl font-bold tracking-tight text-foreground">
        Rekap Nilai Tugas &amp; Kuis.
      </h1>
      <p className="text-secondary text-sm sm:text-base mt-3 max-w-2xl leading-relaxed font-sans">
        Pantau status penilaian tugas per pertemuan dari seluruh mata kuliah
        aktif. Server web menarik data dari endpoint{" "}
        <code className="font-mono text-[13px] text-[#08738a]">
          /v1/elearning/grades
        </code>{" "}
        pada backend UBSI API lokal Anda — tanpa konfigurasi tambahan.
      </p>

      {/* Aksi */}
      <div className="glass-card-3d p-6 sm:p-7 mt-8">
        <div className="flex flex-wrap items-center gap-4">
          <button
            onClick={load}
            disabled={loading}
            className="inline-flex items-center justify-center px-6 py-2.5 rounded-md bg-accent hover:bg-accent-hover text-accent-dark font-semibold text-sm transition-all duration-200 ease-glass disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {loading ? "Memuat…" : hasData ? "Muat Ulang" : "Muat Rekap"}
          </button>
          <p className="text-[11px] font-mono text-secondary leading-relaxed">
            {backend ? (
              <>
                Backend: {backend}
                {meta && (
                  <>
                    {" · "}
                    Sumber: {meta.stale ? "cache (stale)" : meta.cached ? "cache" : "live"}
                    {" · "}
                    {meta.fetchedAt}
                  </>
                )}
              </>
            ) : (
              "Alamat backend dan API key dibaca otomatis dari sisi server (.env)."
            )}
          </p>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div
          role="alert"
          className="mt-6 rounded-md border border-amber-300/70 bg-amber-50/80 px-5 py-4"
        >
          <p className="text-sm font-semibold text-[#92400e]">{error.title}</p>
          <p className="mt-1 text-sm leading-relaxed text-[#a16207]">{error.hint}</p>
        </div>
      )}

      {/* Empty state */}
      {!hasData && !error && !loading && (
        <div className="glass-card mt-6 p-6">
          <p className="text-sm leading-relaxed text-secondary">
            Tekan &ldquo;Muat Rekap&rdquo; untuk menarik data. Pastikan backend
            berjalan dengan kredensial Elearning terisi di{" "}
            <code className="font-mono text-[13px] text-[#08738a]">.env</code> —
            pengambilan pertama memerlukan login ke MyBest, biasanya 10–30 detik.
          </p>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <p className="mt-6 font-mono text-sm text-secondary" aria-live="polite">
          Mengambil data dari server — pengambilan pertama memerlukan login dan
          parsing seluruh mata kuliah, biasanya 10–30 detik…
        </p>
      )}

      {hasData && data && (
        <>
          {/* Ringkasan */}
          <div className="mt-12">
            <h2 className="font-display text-lg font-semibold text-foreground">
              Ringkasan
            </h2>
            <div className="mt-4 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-x-6 gap-y-5">
              {[
                { value: fmt(data.rata_nilai), label: "Rata-rata Nilai" },
                { value: fmt(data.nilai_max), label: "Nilai Tertinggi" },
                { value: fmt(data.nilai_min), label: "Nilai Terendah" },
                { value: String(data.sudah_dinilai), label: "Sudah Dinilai" },
                { value: String(data.belum_dinilai), label: "Belum Dinilai" },
              ].map((s) => (
                <div key={s.label} className="border-l-[3px] border-[#92EEFF] pl-4">
                  <span className="mb-1 block font-display text-2xl font-bold text-foreground">
                    {s.value}
                  </span>
                  <span className="text-[11px] font-mono text-secondary uppercase tracking-wide">
                    {s.label}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Per Pertemuan */}
          <section className="mt-12">
            <h2 className="font-display text-lg font-semibold text-foreground">
              Nilai per Pertemuan
            </h2>
            <div className="glass-card mt-4 overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-stroke bg-white/40">
                    <th className={thClass}>Pertemuan</th>
                    <th className={thClass}>Tugas</th>
                    <th className={thClass}>Dinilai</th>
                    <th className={thClass}>Belum</th>
                    <th className={thClass}>Rata-rata</th>
                    <th className={thClass}>Rentang</th>
                  </tr>
                </thead>
                <tbody className="font-mono text-foreground">
                  {data.per_pertemuan.map((row) => (
                    <tr key={row.pertemuan} className="border-b border-stroke/60 last:border-0">
                      <td className={`${tdClass} font-sans font-medium`}>{row.pertemuan}</td>
                      <td className={tdClass}>{row.total_tugas}</td>
                      <td className={tdClass}>{row.sudah_dinilai}</td>
                      <td className={tdClass}>
                        {row.belum_dinilai > 0 ? (
                          <span className="text-amber-600">{row.belum_dinilai}</span>
                        ) : (
                          <span>0</span>
                        )}
                      </td>
                      <td className={`${tdClass} font-semibold`}>{fmt(row.rata_nilai)}</td>
                      <td className={`${tdClass} text-secondary`}>
                        {row.nilai_min === null || row.nilai_max === null
                          ? "—"
                          : `${fmt(row.nilai_min)} – ${fmt(row.nilai_max)}`}
                      </td>
                    </tr>
                  ))}
                  {data.per_pertemuan.length === 0 && (
                    <tr>
                      <td colSpan={6} className="px-5 py-6 text-center font-sans text-secondary">
                        Belum ada data submission untuk mata kuliah aktif.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>

          {/* Per Mata Kuliah */}
          <section className="mt-12">
            <h2 className="font-display text-lg font-semibold text-foreground">
              Rata-rata per Mata Kuliah
            </h2>
            <div className="glass-card mt-4 overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-stroke bg-white/40">
                    <th className={thClass}>Kode</th>
                    <th className={thClass}>Mata Kuliah</th>
                    <th className={thClass}>Total Tugas</th>
                    <th className={thClass}>Rata-rata</th>
                  </tr>
                </thead>
                <tbody className="font-mono text-foreground">
                  {Object.entries(data.per_matkul).map(([kode, stat]) => (
                    <tr key={kode} className="border-b border-stroke/60 last:border-0">
                      <td className={tdClass}>{kode}</td>
                      <td className={`${tdClass} font-sans text-secondary`}>
                        {courseNames[kode] ?? "—"}
                      </td>
                      <td className={tdClass}>{stat.total_tugas}</td>
                      <td className={`${tdClass} font-semibold`}>{fmt(stat.rata_nilai)}</td>
                    </tr>
                  ))}
                  {Object.keys(data.per_matkul).length === 0 && (
                    <tr>
                      <td colSpan={4} className="px-5 py-6 text-center font-sans text-secondary">
                        Belum ada nilai yang tercatat.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>

          {/* Jadwal Kuis */}
          {data.kuis.length > 0 && (
            <section className="mt-12">
              <h2 className="font-display text-lg font-semibold text-foreground">
                Jadwal Kuis &amp; Ujian
              </h2>
              <div className="glass-card mt-4 overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-stroke bg-white/40">
                      <th className={thClass}>Paket</th>
                      <th className={thClass}>Kode</th>
                      <th className={thClass}>Dosen</th>
                      <th className={thClass}>Mulai</th>
                      <th className={thClass}>Selesai</th>
                    </tr>
                  </thead>
                  <tbody className="font-mono text-foreground">
                    {data.kuis.map((q, i) => (
                      <tr key={`${q.paket}-${q.kode_mtk}-${i}`} className="border-b border-stroke/60 last:border-0">
                        <td className={tdClass}>{q.paket ?? "—"}</td>
                        <td className={tdClass}>{q.kode_mtk ?? "—"}</td>
                        <td className={`${tdClass} font-sans`}>{q.dosen ?? "—"}</td>
                        <td className={`${tdClass} text-secondary`}>{q.ujian_mulai ?? "—"}</td>
                        <td className={`${tdClass} text-secondary`}>{q.ujian_selesai ?? "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}

          {/* Rincian Tugas */}
          {submissions.length > 0 && (
            <section className="mt-12">
              <h2 className="font-display text-lg font-semibold text-foreground">
                Rincian Tugas
              </h2>
              <div className="glass-card mt-4 overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-stroke bg-white/40">
                      <th className={thClass}>Kode</th>
                      <th className={thClass}>Judul</th>
                      <th className={thClass}>Pertemuan</th>
                      <th className={thClass}>Nilai</th>
                      <th className={thClass}>Komentar Dosen</th>
                    </tr>
                  </thead>
                  <tbody className="text-foreground">
                    {submissions.map((s) => (
                      <tr key={s.id} className="border-b border-stroke/60 last:border-0">
                        <td className={`${tdClass} font-mono`}>{s.kode}</td>
                        <td className={`${tdClass} font-medium`}>{s.judul}</td>
                        <td className={`${tdClass} font-mono text-secondary`}>{s.pertemuan}</td>
                        <td className={`${tdClass} font-mono font-semibold`}>
                          {s.nilai === null ? (
                            <span className="font-sans font-normal text-secondary">Belum dinilai</span>
                          ) : (
                            fmt(s.nilai)
                          )}
                        </td>
                        <td className="px-5 py-3 max-w-xs truncate font-sans text-secondary" title={s.komentar_dosen ?? undefined}>
                          {s.komentar_dosen ?? "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}
        </>
      )}
    </div>
  );
}
