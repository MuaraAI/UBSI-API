"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Monogram } from "./Monogram";

export function Navbar({ starsCount = 2 }: { starsCount?: number }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

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
    <header className="sticky top-0 z-50 w-full py-3 px-4 sm:px-6">
      <div
        className={`max-w-5xl mx-auto glass-pill px-5 h-14 flex items-center justify-between transition-all duration-300 ease-glass ${
          scrolled ? "shadow-glass-lg" : ""
        }`}
      >
        <Link href="/" className="flex items-center gap-3 group focus:outline-none">
          <Monogram className="w-7 h-7 group-hover:scale-105 transition-transform" />
          <div className="flex flex-col">
            <span className="font-display font-bold text-base tracking-tight text-foreground">
              UBSI API
            </span>
            <span className="text-[10px] font-mono tracking-widest text-[#08738a] font-bold uppercase -mt-0.5">
              Muara AI
            </span>
          </div>
        </Link>

        <div className="flex items-center gap-3 sm:gap-5">
          <nav className="hidden md:flex items-center gap-5 text-sm text-secondary">
            <a href="#showcase" className="hover:text-foreground transition-colors duration-200 ease-glass">
              Showcase
            </a>
            <a href="#modules" className="hover:text-foreground transition-colors duration-200 ease-glass">
              Modul
            </a>
            <a href="#quickstart" className="hover:text-foreground transition-colors duration-200 ease-glass">
              Quickstart
            </a>
            <a href="#contributors" className="hover:text-foreground transition-colors duration-200 ease-glass">
              Kontributor
            </a>
          </nav>

          <a
            href="https://github.com/MuaraAI/UBSI-API"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-pill bg-[#0a1220] hover:bg-[#131b26] border border-[#92EEFF]/30 text-xs font-mono text-white transition-all duration-200 ease-glass shadow-sm"
            aria-label="GitHub Repository Stars"
          >
            {/* FontAwesome Star Icon (fa-solid fa-star) */}
            <svg
              className="w-3.5 h-3.5 text-[#92EEFF] fill-current"
              viewBox="0 0 576 512"
              aria-hidden="true"
            >
              <path d="M316.9 18C311.6 7 300.4 0 288.1 0s-23.4 7-28.8 18L195 150.3 51.4 171.5c-12 1.8-22 10.2-25.7 21.7s-.7 24.2 7.9 32.7L137.8 329 113.2 474.7c-2 12 3 24.2 12.9 31.3s23 8 33.8 2.3l128.3-68.5 128.3 68.5c10.8 5.7 23.9 4.9 33.8-2.3s14.9-19.3 12.9-31.3L438.5 329 542.7 225.9c8.6-8.5 11.7-21.2 7.9-32.7s-13.7-19.9-25.7-21.7L381.2 150.3 316.9 18z" />
            </svg>
            <span className="text-[#92EEFF] font-bold">{starsCount}</span>
          </a>

          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-expanded={mobileMenuOpen}
            aria-controls="mobile-menu"
            className="md:hidden p-2 rounded-card bg-white/40 border border-stroke text-foreground hover:text-accent transition-colors"
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
        <div
          id="mobile-menu"
          className="md:hidden mt-2 max-w-5xl mx-auto glass-card px-5 py-4 space-y-2"
        >
          <a
            href="#showcase"
            onClick={() => setMobileMenuOpen(false)}
            className="block text-sm font-medium text-secondary hover:text-accent py-1.5 transition-colors"
          >
            Showcase
          </a>
          <a
            href="#modules"
            onClick={() => setMobileMenuOpen(false)}
            className="block text-sm font-medium text-secondary hover:text-accent py-1.5 transition-colors"
          >
            Modul Layanan
          </a>
          <a
            href="#quickstart"
            onClick={() => setMobileMenuOpen(false)}
            className="block text-sm font-medium text-secondary hover:text-accent py-1.5 transition-colors"
          >
            Quickstart (Instalasi)
          </a>
          <a
            href="#contributors"
            onClick={() => setMobileMenuOpen(false)}
            className="block text-sm font-medium text-secondary hover:text-accent py-1.5 transition-colors"
          >
            Kontributor Mahasiswa
          </a>
        </div>
      )}
    </header>
  );
}
