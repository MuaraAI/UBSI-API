import React from "react";
import { CAMPUS_MODULES } from "@/data/modules";

export function ModulesGrid() {
  return (
    <section id="modules" className="py-16 px-4 sm:px-6 max-w-7xl mx-auto">
      <div className="text-center mb-12">
        <span className="text-xs font-mono text-[#2DD4BF] tracking-widest uppercase">
          MODULAR ENDPOINTS
        </span>
        <h2 className="font-display text-2xl sm:text-3xl font-bold text-[#E6EDF3] mt-2">
          6 Layanan Kampus UBSI dalam Satu Standar.
        </h2>
        <p className="text-[#94A7BC] text-sm sm:text-base mt-2 max-w-2xl mx-auto font-sans">
          Setiap modul dilengkapi isolasi parser, caching otomatis dua tingkat, dan mitigasi anti-blokir.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {CAMPUS_MODULES.map((mod) => (
          <div
            key={mod.id}
            className="rounded-lg bg-[#111C2E] border border-white/5 p-6 hover:border-[#2DD4BF]/40 transition-colors flex flex-col justify-between group shadow-sm"
          >
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-mono text-[#2DD4BF] bg-[#0A1220] px-2.5 py-1 rounded border border-[#2DD4BF]/20">
                  {mod.endpointsCount} Endpoints
                </span>
                <span className="text-[11px] font-mono text-[#94A7BC]">
                  {mod.service}
                </span>
              </div>

              <h3 className="font-display text-lg font-semibold text-[#E6EDF3] group-hover:text-[#2DD4BF] transition-colors">
                {mod.name}
              </h3>
              <p className="text-xs sm:text-sm text-[#94A7BC] mt-2 leading-relaxed font-sans">
                {mod.description}
              </p>
            </div>

            <div className="mt-6 pt-4 border-t border-white/5">
              <span className="text-[11px] font-mono text-[#94A7BC] block mb-2">
                CONTOH ENDPOINT:
              </span>
              <div className="flex flex-wrap gap-1.5">
                {mod.endpoints.slice(0, 2).map((ep) => (
                  <code
                    key={ep}
                    className="text-[10px] font-mono bg-[#0A1220] text-[#E6EDF3] px-2 py-0.5 rounded border border-white/5"
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
