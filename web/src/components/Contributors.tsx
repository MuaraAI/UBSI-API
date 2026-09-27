import React from "react";
import Image from "next/image";
import { CONTRIBUTORS } from "@/data/contributors";

export function Contributors({
  contributions = {},
}: {
  contributions?: { [username: string]: number };
}) {
  return (
    <section id="contributors" className="py-16 px-4 sm:px-6 max-w-7xl mx-auto">
      <div className="text-center mb-12">
        <span className="text-xs font-mono text-[#2DD4BF] tracking-widest uppercase">
          OPEN SOURCE COLLABORATION
        </span>
        <h2 className="font-display text-2xl sm:text-3xl font-bold text-[#E6EDF3] mt-2">
          Dibangun oleh Mahasiswa, untuk Komunitas.
        </h2>
        <p className="text-[#94A7BC] text-sm sm:text-base mt-2 max-w-xl mx-auto font-sans">
          Dikembangkan secara independen oleh mahasiswa Informatika UBSI Pontianak di bawah naungan inisiatif Muara AI.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-3xl mx-auto">
        {CONTRIBUTORS.map((c) => {
          const liveCommits = contributions[c.username] ?? c.fallbackCommits;

          return (
            <div
              key={c.username}
              className="rounded-lg bg-[#111C2E] border border-white/5 p-6 flex items-start gap-4 hover:border-[#2DD4BF]/40 transition-colors shadow-sm"
            >
              <Image
                src={c.avatarUrl}
                alt={c.name}
                width={64}
                height={64}
                className="rounded-full border border-[#2DD4BF]/30 shrink-0 bg-[#0A1220]"
              />

              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <h3 className="font-display font-semibold text-base text-[#E6EDF3] truncate">
                    {c.name}
                  </h3>
                  <span className="text-xs font-mono text-[#2DD4BF] bg-[#0A1220] px-2 py-0.5 rounded border border-[#2DD4BF]/20">
                    {liveCommits} Commits
                  </span>
                </div>

                <a
                  href={c.profileUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs font-mono text-[#94A7BC] hover:text-[#54E3D1] transition-colors block -mt-0.5"
                >
                  @{c.username}
                </a>

                <p className="text-xs font-medium text-[#2DD4BF] mt-2">
                  {c.role}
                </p>

                <div className="mt-2 text-[11px] font-mono text-[#94A7BC] leading-relaxed">
                  <div>Prodi: {c.prodi} • {c.kelas}</div>
                  <div>NIM: {c.nim}</div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-8 text-center">
        <a
          href="https://github.com/MuaraAI/UBSI-API/blob/main/CONTRIBUTING.md"
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs font-mono text-[#94A7BC] hover:text-[#2DD4BF] underline underline-offset-4 transition-colors"
        >
          Ingin berkontribusi pada pengembangan UBSI API? Baca panduan di CONTRIBUTING.md →
        </a>
      </div>
    </section>
  );
}
