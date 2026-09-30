import React from "react";
import { CAMPUS_MODULES } from "@/data/modules";

export function ModulesGrid() {
  return (
    <section id="modules" className="py-16 px-4 sm:px-6 max-w-7xl mx-auto">
      <div className="text-left mb-12">
        <div className="badge-dark mb-4">
          <span className="w-2 h-2 rounded-full bg-[#92EEFF] shadow-[0_0_8px_#92EEFF] animate-pulse" />
          <span>MODULAR ENDPOINTS</span>
        </div>
        <h2 className="font-display text-2xl sm:text-3xl font-bold text-foreground mt-3">
          6 Layanan Kampus UBSI dalam Satu Standar.
        </h2>
        <p className="text-secondary text-sm sm:text-base mt-2 max-w-2xl font-sans">
          Setiap modul dilengkapi isolasi parser, caching otomatis dua tingkat, dan mitigasi anti-blokir.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {CAMPUS_MODULES.map((mod) => (
          <div
            key={mod.id}
            className="glass-card-3d p-6 flex flex-col justify-between group relative overflow-hidden"
          >
            <div className="absolute inset-0 rounded-[20px] bg-gradient-to-br from-white/60 via-transparent to-cyan-100/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
            <div className="relative z-10">
              <div className="flex items-center justify-between mb-4">
                <span className="accent-badge text-xs font-mono font-semibold">
                  {mod.endpointsCount} Endpoints
                </span>
                <span className="text-[11px] font-mono text-secondary font-medium">
                  {mod.service}
                </span>
              </div>

              <h3 className="font-display text-lg font-semibold text-foreground group-hover:text-[#00778c] transition-colors duration-200">
                {mod.name}
              </h3>
              <p className="text-xs sm:text-sm text-secondary mt-2 leading-relaxed font-sans">
                {mod.description}
              </p>
            </div>

            <div className="mt-6 pt-4 border-t border-stroke relative z-10">
              <span className="text-[11px] font-mono text-secondary block mb-2 font-medium">
                CONTOH ENDPOINT:
              </span>
              <div className="flex flex-wrap gap-1.5">
                {mod.endpoints.slice(0, 2).map((ep) => (
                  <code
                    key={ep}
                    className="text-[11px] font-mono bg-[#0c1421] text-[#92EEFF] px-2.5 py-1 rounded-md border border-[#92EEFF]/20 group-hover:border-[#92EEFF]/50 transition-colors"
                  >
                    {ep}
                  </code>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
