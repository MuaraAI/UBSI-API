import React from "react";

export function Hero() {
  return (
    <section className="relative pt-12 pb-14 sm:pt-20 sm:pb-20 md:pt-28 md:pb-24 px-4 sm:px-6 max-w-7xl mx-auto text-center">
      <div className="badge-dark mb-6 mx-auto">
        <span className="w-2 h-2 rounded-full bg-[#92EEFF] shadow-[0_0_8px_#92EEFF] animate-pulse" />
        <span>UNOFFICIAL CAMPUS GATEWAY</span>
      </div>

      <h1 className="font-display text-3xl sm:text-5xl md:text-6xl font-bold tracking-tight text-foreground max-w-4xl mx-auto leading-[1.1] mb-6">
        Satu Antarmuka REST API untuk Seluruh Layanan Kampus UBSI.
      </h1>

      <p className="text-secondary text-base sm:text-lg md:text-xl max-w-2xl mx-auto leading-relaxed mb-10 font-sans">
        Agregator data modern berkecepatan tinggi untuk SIAKAD, MyBest Elearning, E-Library,
        Repository, dan E-Journal dengan format JSON terstandarisasi dan Redis cache sub-250ms.
      </p>

      <div className="flex flex-wrap items-center justify-center gap-4 w-full sm:w-auto">
        <a
          href="#showcase"
          className="w-full sm:w-auto inline-flex items-center justify-center px-7 py-3.5 rounded-pill bg-accent hover:bg-accent-hover text-accent-dark font-semibold text-sm transition-all duration-200 ease-glass shadow-float"
        >
          Lihat Contoh Response
        </a>
        <a
          href="https://github.com/MuaraAI/UBSI-API"
          target="_blank"
          rel="noopener noreferrer"
          className="w-full sm:w-auto inline-flex items-center justify-center px-7 py-3.5 rounded-pill glass-card text-foreground font-semibold text-sm hover:border-accent/30 transition-all duration-200 ease-glass"
        >
          GitHub Repository
        </a>
      </div>

      <div className="mt-14 grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4 max-w-3xl mx-auto">
        <div className="glass-card-3d px-4 py-3.5 text-xs font-mono text-secondary">
          <span className="text-[#083344] font-bold block text-lg mb-0.5">6 Layanan</span>
          Terintegrasi
        </div>
        <div className="glass-card-3d px-4 py-3.5 text-xs font-mono text-secondary">
          <span className="text-[#083344] font-bold block text-lg mb-0.5">23 Jurnal</span>
          Aktif Resmi
        </div>
        <div className="glass-card-3d px-4 py-3.5 text-xs font-mono text-secondary">
          <span className="text-[#083344] font-bold block text-lg mb-0.5">Sub-250ms</span>
          Caching Latency
        </div>
        <div className="glass-card-3d px-4 py-3.5 text-xs font-mono text-secondary">
          <span className="text-[#083344] font-bold block text-lg mb-0.5">71 Tests</span>
          100% Passed
        </div>
      </div>
    </section>
  );
}
