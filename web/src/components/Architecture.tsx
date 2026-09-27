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
      <div className="rounded-lg bg-[#0A1220] border border-white/10 p-8 sm:p-12 shadow-float">
        <div className="text-center mb-10">
          <span className="text-xs font-mono text-[#2DD4BF] tracking-widest uppercase">
            ENGINEERING EXCELLENCE
          </span>
          <h2 className="font-display text-2xl sm:text-3xl font-bold text-[#E6EDF3] mt-2">
            Dibangun untuk Keandalan dan Kecepatan.
          </h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {specs.map((s, idx) => (
            <div
              key={idx}
              className="p-5 rounded-md bg-[#111C2E] border border-white/5 flex flex-col justify-between"
            >
              <div>
                <span className="font-display text-2xl font-bold text-[#2DD4BF]">
                  {s.metric}
                </span>
                <h3 className="font-display text-sm font-semibold text-[#E6EDF3] mt-1">
                  {s.title}
                </h3>
                <p className="text-xs text-[#94A7BC] mt-2 leading-relaxed font-sans">
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
