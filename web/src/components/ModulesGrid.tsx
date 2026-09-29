import React from "react";
import { CAMPUS_MODULES } from "@/data/modules";

export function ModulesGrid() {
  return (
    <section id="modules" className="py-16 px-4 sm:px-6 max-w-7xl mx-auto">
      <div className="text-center mb-12">
        <span className="accent-badge text-xs font-mono tracking-widest uppercase">
          MODULAR ENDPOINTS
        </span>
        <h2 className="font-display text-2xl sm:text-3xl font-bold text-foreground mt-3">
          6 Layanan Kampus UBSI dalam Satu Standar.
        </h2>
        <p className="text-secondary text-sm sm:text-base mt-2 max-w-2xl mx-auto font-sans">
          Setiap modul dilengkapi isolasi parser, caching otomatis dua tingkat, dan mitigasi anti-blokir.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {CAMPUS_MODULES.map((mod) => (
          <div
            key={mod.id}
            className="glass-card p-6 flex flex-col justify-between group"
          >
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="accent-badge text-xs font-mono">
                  {mod.endpointsCount} Endpoints
                </span>
                <span className="text-[11px] font-mono text-secondary">
                  {mod.service}
                </span>
              </div>

              <h3 className="font-display text-lg font-semibold text-foreground group-hover:text-accent transition-colors duration-200 ease-glass">
                {mod.name}
              </h3>
              <p className="text-xs sm:text-sm text-secondary mt-2 leading-relaxed font-sans">
                {mod.description}
              </p>
            </div>

            <div className="mt-6 pt-4 border-t border-stroke">
              <span className="text-[11px] font-mono text-secondary block mb-2">
                CONTOH ENDPOINT:
              </span>
              <div className="flex flex-wrap gap-1.5">
                {mod.endpoints.slice(0, 2).map((ep) => (
                  <code
                    key={ep}
                    className="text-[10px] font-mono bg-code-bg text-code-text px-2 py-0.5 rounded-sm border border-white/10"
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
