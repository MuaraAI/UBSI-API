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
      <div className="text-left mb-12">
        <div className="badge-dark mb-4">
          <span className="w-2 h-2 rounded-full bg-[#92EEFF] shadow-[0_0_8px_#92EEFF] animate-pulse" />
          <span>OPEN SOURCE COLLABORATION</span>
        </div>
        <h2 className="font-display text-2xl sm:text-3xl font-bold text-foreground mt-3">
          Dibangun oleh Mahasiswa, untuk Komunitas.
        </h2>
        <p className="text-secondary text-sm sm:text-base mt-2 max-w-xl font-sans">
          Dikembangkan secara independen oleh mahasiswa Informatika UBSI Pontianak di bawah naungan inisiatif Muara AI.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-3xl mx-auto">
        {CONTRIBUTORS.map((c) => {
          const liveCommits = contributions[c.username] ?? c.fallbackCommits;

          return (
            <div
              key={c.username}
              className="glass-card-3d p-6 flex items-start gap-4 group"
            >
              <Image
                src={c.avatarUrl}
                alt={c.name}
                width={64}
                height={64}
                className="rounded-full border-2 border-[#92EEFF]/40 shrink-0 bg-white/50"
              />

              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <h3 className="font-display font-semibold text-base text-foreground truncate">
                    {c.name}
                  </h3>
                  <span className="accent-badge text-xs font-mono font-semibold">
                    {liveCommits} Commits
                  </span>
                </div>

                <a
                  href={c.profileUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs font-mono text-secondary hover:text-[#00778c] transition-colors duration-200 block -mt-0.5"
                >
                  @{c.username}
                </a>

                <p className="text-xs font-semibold text-[#00778c] mt-2">
                  {c.role}
                </p>

                <div className="mt-2 text-[11px] font-mono text-secondary leading-relaxed">
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
          className="text-xs font-mono text-secondary hover:text-accent underline underline-offset-4 transition-colors duration-200"
        >
          Ingin berkontribusi pada pengembangan UBSI API? Baca panduan di CONTRIBUTING.md →
        </a>
      </div>
    </section>
  );
}
