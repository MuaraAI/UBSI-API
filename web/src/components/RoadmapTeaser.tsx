import React from "react";
import { ROADMAP_ITEMS } from "@/data/roadmap";

export function RoadmapTeaser() {
  return (
    <section className="py-16 px-4 sm:px-6 max-w-7xl mx-auto">
      <div className="text-center mb-10">
        <span className="accent-badge text-xs font-mono tracking-widest uppercase">
          WHAT\u2019S NEXT
        </span>
        <h2 className="font-display text-2xl sm:text-3xl font-bold text-foreground mt-3">
          Roadmap v1.2: Fitur Produktivitas Mahasiswa.
        </h2>
        <p className="text-secondary text-sm sm:text-base mt-2 max-w-xl mx-auto font-sans">
          Fitur yang sedang dipersiapkan untuk memudahkan rutinitas perkuliahan harian civitas UBSI.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {ROADMAP_ITEMS.map((item, idx) => (
          <div
            key={idx}
            className="glass-card p-6 flex flex-col justify-between group"
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

              <h3 className="font-display text-base font-semibold text-foreground group-hover:text-accent transition-colors duration-200 ease-glass">
                {item.title}
              </h3>
              <p className="text-xs text-secondary mt-2 leading-relaxed font-sans">
                {item.description}
              </p>
            </div>

            <div className="mt-4 pt-3 border-t border-stroke flex items-center justify-between text-[11px] font-mono text-secondary">
              <span>Status:</span>
              <span className="text-accent capitalize">{item.status}</span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
