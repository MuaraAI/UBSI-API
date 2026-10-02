import React from "react";
import Link from "next/link";
import { ROADMAP_ITEMS } from "@/data/roadmap";

const STATUS_DOT: Record<string, string> = {
  tersedia: "bg-emerald-500",
  upcoming: "bg-amber-500",
  "in-progress": "bg-[#08738a]",
  planned: "bg-zinc-400",
};

export function RoadmapTeaser() {
  return (
    <section className="py-16 px-4 sm:px-6 max-w-7xl mx-auto">
      <div className="text-left mb-10">
        <p className="section-kicker mb-3">What&rsquo;s Next</p>
        <h2 className="font-display text-2xl sm:text-3xl font-bold text-foreground">
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
              <span className="text-xs font-mono text-secondary">{item.version}</span>

              <h3 className="font-display text-base font-semibold text-foreground group-hover:text-[#00778c] transition-colors duration-200 mt-2">
                {item.title}
              </h3>
              <p className="text-xs text-secondary mt-2 leading-relaxed font-sans">
                {item.description}
              </p>
            </div>

            <div className="mt-4 pt-3 border-t border-stroke">
              <div className="flex items-center justify-between text-[11px] font-mono text-secondary">
                <span className="flex items-center gap-1.5">
                  <span
                    className={`w-1.5 h-1.5 rounded-full ${STATUS_DOT[item.status] ?? "bg-zinc-400"}`}
                    aria-hidden="true"
                  />
                  Status
                </span>
                <span className="text-[#08738a] font-semibold capitalize">{item.status}</span>
              </div>
              {item.href && (
                <Link
                  href={item.href}
                  className="mt-2.5 inline-block text-[11px] font-mono font-semibold text-[#08738a] hover:text-foreground underline underline-offset-4 decoration-[#92EEFF] transition-colors duration-200"
                >
                  Buka halaman &rarr;
                </Link>
              )}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
