"use client";

import React, { useEffect, useRef } from "react";
import anime from "animejs";
import { DeepWaterLink } from "./DeepWaterButton";

export function Hero() {
  const heroRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const prefersReducedMotion = window.matchMedia(
      "(prefers-reduced-motion: reduce)"
    ).matches;

    if (!prefersReducedMotion && heroRef.current) {
      anime({
        targets: heroRef.current.querySelectorAll(".anime-reveal"),
        opacity: [0, 1],
        translateY: [20, 0],
        delay: anime.stagger(100),
        duration: 700,
        easing: "cubicBezier(0.2, 0, 0, 1)",
      });
    }
  }, []);

  return (
    <section
      ref={heroRef}
      className="relative overflow-hidden pt-10 pb-12 sm:pt-16 sm:pb-16 md:pt-24 md:pb-20 px-4 sm:px-6 max-w-7xl mx-auto text-center flex flex-col items-center"
    >
      <div
        className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-[#2DD4BF]/10 rounded-full blur-3xl pointer-events-none -z-10"
        aria-hidden="true"
      />

      <div className="anime-reveal inline-flex items-center gap-2 text-xs font-mono tracking-widest text-[#2DD4BF] uppercase mb-4 font-semibold">
        <span>UNOFFICIAL CAMPUS GATEWAY</span>
      </div>

      <h1 className="anime-reveal font-display text-3xl sm:text-5xl md:text-6xl font-bold tracking-tight text-[#E6EDF3] max-w-4xl leading-[1.1] mb-6">
        Satu Antarmuka REST API untuk Seluruh Layanan Kampus UBSI.
      </h1>

      <p className="anime-reveal text-[#94A7BC] text-base sm:text-lg md:text-xl max-w-2xl leading-relaxed mb-10 font-sans">
        Agregator data modern berkecepatan tinggi untuk SIAKAD, MyBest Elearning, E-Library,
        Repository, dan E-Journal dengan format JSON terstandarisasi dan Redis cache sub-250ms.
      </p>

      <div className="anime-reveal flex flex-wrap items-center justify-center gap-4 w-full sm:w-auto">
        <DeepWaterLink href="#showcase" variant="primary" size="lg" shine>
          Lihat Contoh Response
          <svg
            className="w-4 h-4 transition-transform duration-200 group-hover:translate-x-1"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
            aria-hidden="true"
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5-5 5M6 12h12" />
          </svg>
        </DeepWaterLink>
        <DeepWaterLink
          href="https://github.com/MuaraAI/UBSI-API"
          target="_blank"
          rel="noopener noreferrer"
          variant="secondary"
          size="lg"
        >
          GitHub Repository
        </DeepWaterLink>
      </div>

      <div className="anime-reveal mt-12 grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs font-mono text-[#94A7BC]">
        <div className="px-4 py-2.5 rounded-md bg-[#111C2E]/60 border border-white/5">
          <span className="text-[#2DD4BF] font-bold">6 Layanan</span> Terintegrasi
        </div>
        <div className="px-4 py-2.5 rounded-md bg-[#111C2E]/60 border border-white/5">
          <span className="text-[#2DD4BF] font-bold">23 Jurnal</span> Aktif Resmi
        </div>
        <div className="px-4 py-2.5 rounded-md bg-[#111C2E]/60 border border-white/5">
          <span className="text-[#2DD4BF] font-bold">Sub-250ms</span> Caching Latency
        </div>
        <div className="px-4 py-2.5 rounded-md bg-[#111C2E]/60 border border-white/5">
          <span className="text-[#2DD4BF] font-bold">71 Tests</span> 100% Passed
        </div>
      </div>
    </section>
  );
}
