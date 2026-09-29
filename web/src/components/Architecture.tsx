import React from "react";

export function Architecture() {
  const specs = [
    {
      title: "Redis SWR Caching",
      metric: "Sub-250ms",
      desc: "Caching dua tingkat (Redis DB 2) dengan latar belakang Stale-While-Revalidate untuk performa instant.",
    },
    {
      title: "Katalog OJS Lengkap",
      metric: "23 Jurnal",
      desc: "Penangkapan otomatis seluruh jurnal resmi aktif kampus dengan pemulihan judul murni dari server OJS.",
    },
    {
      title: "Headless Scrapling",
      metric: "Anti-Ban",
      desc: "Parser modern berbasis Scrapling v0.9+ dengan fingerprint Chrome TLS dan simulasi browser nyata.",
    },
    {
      title: "Zero-Secret Storage",
      metric: "Stateless",
      desc: "Tidak ada penyimpanan kredensial mahasiswa di basis data; otentikasi sesi terenkripsi penuh.",
    },
  ];

  return (
    <section className="py-16 px-4 sm:px-6 max-w-7xl mx-auto">
      <div className="glass-card p-8 sm:p-12">
        <div className="text-center mb-10">
          <span className="accent-badge text-xs font-mono tracking-widest uppercase">
            ENGINEERING EXCELLENCE
          </span>
          <h2 className="font-display text-2xl sm:text-3xl font-bold text-foreground mt-3">
            Dibangun untuk Keandalan dan Kecepatan.
          </h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {specs.map((s, idx) => (
            <div
              key={idx}
              className="p-5 rounded-card bg-white/40 border border-stroke flex flex-col justify-between hover:bg-white/60 transition-all duration-200 ease-glass"
            >
              <div>
                <span className="font-display text-2xl font-bold text-accent">
                  {s.metric}
                </span>
                <h3 className="font-display text-sm font-semibold text-foreground mt-1">
                  {s.title}
                </h3>
                <p className="text-xs text-secondary mt-2 leading-relaxed font-sans">
                  {s.desc}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
