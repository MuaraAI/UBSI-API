import React from "react";
import { ROADMAP_ITEMS } from "@/data/roadmap";

export function RoadmapTeaser() {
  return (
    <section className="py-16 px-4 sm:px-6 max-w-7xl mx-auto">
      <div className="text-center mb-10">
        <span className="text-xs font-mono text-[#2DD4BF] tracking-widest uppercase">
          WHAT'S NEXT
        </span>
        <h2 className="font-display text-2xl sm:text-3xl font-bold text-[#E6EDF3] mt-2">
          Roadmap v1.2 — Fitur Produktivitas Mahasiswa.
        </h2>
        <p className="text-[#94A7BC] text-sm sm:text-base mt-2 max-w-xl mx-auto font-sans">
          Fitur yang sedang dipersiapkan untuk memudahkan rutinitas perkuliahan harian civitas UBSI.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {ROADMAP_ITEMS.map((item, idx) => (
          <div
            key={idx}
            className="rounded-lg bg-[#111C2E] border border-white/5 p-6 flex flex-col justify-between hover:border-[#2DD4BF]/30 transition-colors shadow-sm"
          >
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] font-mono font-bold text-[#2DD4BF] bg-[#0A1220] px-2 py-0.5 rounded border border-[#2DD4BF]/20 uppercase">
                  {item.badge}
                </span>
                <span className="text-xs font-mono text-[#94A7BC]">
                  {item.version}
                </span>
              </div>

              <h3 className="font-display text-base font-semibold text-[#E6EDF3]">
                {item.title}
              </h3>
              <p className="text-xs text-[#94A7BC] mt-2 leading-relaxed font-sans">
                {item.description}
              </p>
            </div>

            <div className="mt-4 pt-3 border-t border-white/5 flex items-center justify-between text-[11px] font-mono text-[#94A7BC]">
              <span>Status:</span>
              <span className="text-[#54E3D1] capitalize">{item.status}</span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
