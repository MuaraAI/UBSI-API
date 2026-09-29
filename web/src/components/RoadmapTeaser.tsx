import React from "react";
import { ROADMAP_ITEMS } from "@/data/roadmap";

export function RoadmapTeaser() {
  return (
    <section className="py-16 px-4 sm:px-6 max-w-7xl mx-auto">
      <div className="text-left mb-10">
        <div className="badge-dark mb-4">
          <span className="w-2 h-2 rounded-full bg-[#92EEFF] shadow-[0_0_8px_#92EEFF] animate-pulse" />
          <span>WHAT’S NEXT</span>
        </div>
        <h2 className="font-display text-2xl sm:text-3xl font-bold text-foreground mt-3">
          Roadmap v1.2: Fitur Produktivitas Mahasiswa.
        </h2>
        <p className="text-secondary text-sm sm:text-base mt-2 max-w-xl font-sans">
          Fitur yang sedang dipersiapkan untuk memudahkan rutinitas perkuliahan harian civitas UBSI.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {ROADMAP_ITEMS.map((item, idx) => (
          <div
            key={idx}
            className="glass-card-3d p-6 flex flex-col justify-between group"
          >
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="accent-badge text-[10px] font-mono font-bold uppercase">
                  {item.badge}
                </span>
                <span className="text-xs font-mono text-secondary">
                  {item.version}
                </span>
              </div>

              <h3 className="font-display text-base font-semibold text-foreground group-hover:text-[#00778c] transition-colors duration-200">
                {item.title}
              </h3>
              <p className="text-xs text-secondary mt-2 leading-relaxed font-sans">
                {item.description}
              </p>
            </div>

            <div className="mt-4 pt-3 border-t border-stroke flex items-center justify-between text-[11px] font-mono text-secondary">
              <span>Status:</span>
              <span className="text-[#08738a] font-semibold capitalize">{item.status}</span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
