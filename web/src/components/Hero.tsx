import React from "react";

export function Hero() {
  return (
    <section className="relative pt-8 pb-14 sm:pt-14 sm:pb-20 md:pt-20 md:pb-24 px-4 sm:px-6 max-w-7xl mx-auto">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-8 items-center">
        {/* Left column: Text content */}
        <div className="lg:col-span-7 text-left">
          <div className="badge-dark mb-6">
            <span className="w-2 h-2 rounded-full bg-[#92EEFF] shadow-[0_0_8px_#92EEFF] animate-pulse" />
            <span>UNOFFICIAL CAMPUS GATEWAY</span>
          </div>

          <h1 className="font-display text-3xl sm:text-5xl md:text-5xl lg:text-6xl font-bold tracking-tight text-foreground leading-[1.12] mb-6">
            Satu Antarmuka REST API untuk Seluruh Layanan Kampus UBSI.
          </h1>

          <p className="text-secondary text-base sm:text-lg md:text-xl max-w-2xl leading-relaxed mb-8 font-sans">
            Agregator data modern berkecepatan tinggi untuk SIAKAD, MyBest Elearning, E-Library,
            Repository, dan E-Journal dengan format JSON terstandarisasi dan Redis cache sub-250ms.
          </p>

          <div className="flex flex-wrap items-center gap-4 w-full sm:w-auto">
            <a
              href="#showcase"
              className="inline-flex items-center justify-center px-7 py-3.5 rounded-pill bg-accent hover:bg-accent-hover text-accent-dark font-semibold text-sm transition-all duration-200 ease-glass shadow-float"
            >
              Lihat Contoh Response
            </a>
            <a
              href="https://github.com/MuaraAI/UBSI-API"
              target="_blank"
              rel="noopener noreferrer"
              className="uw-button"
            >
              <span>
                <svg
                  className="w-4 h-4 fill-current"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
                </svg>
                GitHub Repository
              </span>
            </a>
          </div>

          <div className="mt-12 grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4 max-w-2xl">
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
        </div>

        {/* Right column: 3D Pyramid Glass Loader (andrew-demchenk0/orange-monkey-2) */}
        <div className="lg:col-span-5 flex flex-col items-center justify-center relative min-h-[380px]">
          <div className="absolute w-80 h-80 rounded-full bg-[#92EEFF]/20 filter blur-3xl pointer-events-none -z-10 animate-pulse" />
          
          <div className="w-full max-w-[390px] rounded-[24px] bg-[#0c1421]/90 backdrop-blur-2xl border border-white/10 shadow-[0_24px_60px_-12px_rgba(10,18,32,0.45),inset_0_1px_1px_rgba(255,255,255,0.15),0_0_28px_rgba(146,238,255,0.14)] p-6 sm:p-7 flex flex-col items-center justify-center relative overflow-hidden group">
            <div className="pyramid-loader">
              <div className="pyramid-wrapper">
                <span className="pyramid-side pyramid-side1" />
                <span className="pyramid-side pyramid-side2" />
                <span className="pyramid-side pyramid-side3" />
                <span className="pyramid-side pyramid-side4" />
                <span className="pyramid-shadow" />
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-white/10 w-full text-left">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-[#92EEFF] shadow-[0_0_8px_#92EEFF] animate-pulse" />
                  <span className="text-xs font-mono font-bold tracking-wider text-[#92EEFF] uppercase">
                    Tentang UBSI API
                  </span>
                </div>
                <span className="text-[10px] font-mono text-[#94A7BC] bg-white/5 px-2 py-0.5 rounded-sm border border-white/10">
                  Open Core • MIT
                </span>
              </div>
              <p className="text-xs text-[#94A7BC] leading-relaxed font-sans">
                REST API aggregator open-source untuk otomasi dan integrasi 6 layanan portal kampus UBSI. Mengonversi data web portal mahasiswa menjadi JSON terstruktur tanpa menyimpan kredensial (stateless) dengan performa sub-250ms Redis cache.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
