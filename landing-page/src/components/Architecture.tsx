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
      <div className="glass-card-3d p-8 sm:p-12">
        <div className="text-left mb-10">
          <p className="section-kicker mb-3">Engineering Excellence</p>
          <h2 className="font-display text-2xl sm:text-3xl font-bold text-foreground">
            Dibangun untuk Keandalan dan Kecepatan.
          </h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {specs.map((s, idx) => (
            <div
              key={idx}
              className="p-5 rounded-[18px] bg-white/50 border border-white/80 shadow-sm flex flex-col justify-between hover:bg-white/80 hover:border-[#92EEFF]/80 hover:shadow-float transition-all duration-300"
            >
              <div>
                <span className="font-display text-2xl font-bold text-[#083344]">
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
