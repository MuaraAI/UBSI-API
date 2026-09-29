"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Monogram } from "./Monogram";
import { DeepWaterLink } from "./DeepWaterButton";

export function Navbar({ starsCount = 2 }: { starsCount?: number }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setMobileMenuOpen(false);
      }
    };

    if (mobileMenuOpen) {
      window.addEventListener("keydown", handleKeyDown);
      return () => window.removeEventListener("keydown", handleKeyDown);
    }
  }, [mobileMenuOpen]);

  return (
    <header className="sticky top-0 z-50 w-full border-b border-white/5 bg-[#0A1220]/90 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
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

        <div className="flex items-center gap-3 sm:gap-6">
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

          <DeepWaterLink
            href="https://github.com/MuaraAI/UBSI-API"
            target="_blank"
            rel="noopener noreferrer"
            variant="secondary"
            size="sm"
            className="border-white/10 hover:border-[#2DD4BF]/40 font-mono"
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
          </DeepWaterLink>

          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-expanded={mobileMenuOpen}
            aria-controls="mobile-menu"
            className="md:hidden p-2 rounded-md bg-[#111C2E] border border-white/10 text-[#E6EDF3] hover:text-[#2DD4BF] transition-colors"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? (
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            )}
          </button>
        </div>
      </div>

      {mobileMenuOpen && (
        <div id="mobile-menu" className="md:hidden border-b border-white/5 bg-[#0D1624] px-4 py-3 space-y-2">
          <a
            href="#showcase"
            onClick={() => setMobileMenuOpen(false)}
            className="block text-sm font-medium text-[#94A7BC] hover:text-[#2DD4BF] py-1 transition-colors"
          >
            Showcase
          </a>
          <a
            href="#modules"
            onClick={() => setMobileMenuOpen(false)}
            className="block text-sm font-medium text-[#94A7BC] hover:text-[#2DD4BF] py-1 transition-colors"
          >
            Modul Layanan
          </a>
          <a
            href="#quickstart"
            onClick={() => setMobileMenuOpen(false)}
            className="block text-sm font-medium text-[#94A7BC] hover:text-[#2DD4BF] py-1 transition-colors"
          >
            Quickstart (Instalasi)
          </a>
          <a
            href="#contributors"
            onClick={() => setMobileMenuOpen(false)}
            className="block text-sm font-medium text-[#94A7BC] hover:text-[#2DD4BF] py-1 transition-colors"
          >
            Kontributor Mahasiswa
          </a>
        </div>
      )}
    </header>
  );
}
