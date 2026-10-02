import React from "react";
import Image from "next/image";
import { CONTRIBUTORS } from "@/data/contributors";

function ArrowUpRightIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      className="h-3.5 w-3.5 shrink-0 text-[#111418] opacity-60 transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
    >
      <path d="M7 17 17 7" />
      <path d="M9 7h8v8" />
    </svg>
  );
}

export function Contributors({
  contributions = {},
}: {
  contributions?: { [username: string]: number };
}) {
  return (
    <section id="contributors" className="w-full scroll-mt-16 bg-[#D5E4FB]">
      <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 sm:py-24">
        <h2 className="font-anton uppercase leading-[0.95] tracking-[0.005em] text-[#111418] text-[40px] sm:text-[56px] sm:leading-[0.93] lg:text-[64px]">
          Dibangun oleh Mahasiswa,
          <br />
          untuk Komunitas.
        </h2>
        <p className="mt-6 max-w-2xl text-[15px] leading-relaxed text-[#2b313c] sm:text-base">
          Dikembangkan secara independen oleh mahasiswa Informatika UBSI
          Pontianak di bawah naungan inisiatif Muara AI. Klik kartu untuk
          membuka profil GitHub.
        </p>

        <div className="mt-10 grid grid-cols-1 gap-5 md:grid-cols-3">
          {CONTRIBUTORS.map((c) => {
            const liveCommits = contributions[c.username] ?? c.fallbackCommits;

            return (
              <a
                key={c.username}
                href={c.profileUrl}
                target="_blank"
                rel="noopener noreferrer"
                aria-label={`Profil GitHub ${c.name}`}
                className="group flex items-center gap-4 rounded-[14px] border-[1.5px] border-[#111827] bg-white p-5 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-[5px_5px_0_0_#111827] focus-visible:outline-[#111827]"
              >
                <Image
                  src={c.avatarUrl}
                  alt={`Avatar ${c.name}`}
                  width={48}
                  height={48}
                  sizes="48px"
                  className="h-12 w-12 shrink-0 rounded-full border-[1.5px] border-[#111827] object-cover"
                />

                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-start justify-between gap-x-3 gap-y-2">
                    <div className="min-w-max max-w-full">
                      <h3 className="flex items-center gap-1 text-[15px] font-bold leading-tight text-[#111418]">
                        <span className="truncate">{c.name}</span>
                        <ArrowUpRightIcon />
                      </h3>
                      <p className="mt-0.5 truncate font-mono text-[11.5px] text-[#6b7280]">
                        @{c.username}
                      </p>
                    </div>
                    <span className="shrink-0 whitespace-nowrap rounded-full border-[1.5px] border-[#111827] bg-[#FFD84D] px-2.5 py-[3px] font-mono text-[11px] font-bold text-[#111827]">
                      {liveCommits} commits
                    </span>
                  </div>

                  <p className="mt-2 text-[12.5px] font-bold text-[#111418]">
                    {c.role}
                  </p>
                  <p className="mt-1 font-mono text-[10.5px] tracking-wide text-[#6b7280]">
                    {c.kelas} &bull; NIM {c.nim}
                  </p>
                </div>
              </a>
            );
          })}
        </div>

        <a
          href="https://github.com/MuaraAI/UBSI-API/blob/main/CONTRIBUTING.md"
          target="_blank"
          rel="noopener noreferrer"
          className="mt-10 inline-block font-mono text-[12.5px] text-[#111418] underline decoration-[1.5px] underline-offset-4 transition-colors duration-200 hover:text-[#39424f]"
        >
          Ingin berkontribusi pada pengembangan UBSI API? Baca panduan di
          CONTRIBUTING.md &rarr;
        </a>
      </div>
    </section>
  );
}
