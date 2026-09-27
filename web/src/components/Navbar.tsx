import React from "react";
import Link from "next/link";
import { Monogram } from "./Monogram";

export function Navbar({ starsCount = 2 }: { starsCount?: number }) {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-white/5 bg-[#0A1220]/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        {/* Brand */}
        <Link href="/" className="flex items-center gap-3 group focus:outline-none">
          <Monogram className="w-8 h-8 group-hover:scale-105 transition-transform" />
          <div className="flex flex-col">
            <span className="font-display font-bold text-lg tracking-tight text-[#E6EDF3]">
              UBSI API
            </span>
            <span className="text-[10px] font-mono tracking-widest text-[#2DD4BF] uppercase -mt-1">
              Muara AI
            </span>
          </div>
        </Link>

        {/* Navigation & Action */}
        <div className="flex items-center gap-6">
          <nav className="hidden md:flex items-center gap-6 text-sm text-[#94A7BC]">
            <a href="#showcase" className="hover:text-[#E6EDF3] transition-colors">
              Showcase
            </a>
            <a href="#modules" className="hover:text-[#E6EDF3] transition-colors">
              Modul
            </a>
            <a href="#quickstart" className="hover:text-[#E6EDF3] transition-colors">
              Quickstart
            </a>
            <a href="#contributors" className="hover:text-[#E6EDF3] transition-colors">
              Kontributor
            </a>
          </nav>

          <a
            href="https://github.com/MuaraAI/UBSI-API"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-3 py-1.5 rounded-md bg-[#111C2E] hover:bg-[#17263D] border border-white/10 hover:border-[#2DD4BF]/40 text-xs font-mono text-[#E6EDF3] transition-all"
            aria-label="GitHub Repository"
          >
            <svg
              className="w-4 h-4 fill-current"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
            </svg>
            <span className="font-semibold">Star</span>
            <span className="text-[#2DD4BF] font-bold">★ {starsCount}</span>
          </a>
        </div>
      </div>
    </header>
  );
}
