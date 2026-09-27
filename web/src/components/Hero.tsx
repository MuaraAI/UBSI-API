"use client";

import React, { useEffect, useRef } from "react";
import anime from "animejs";

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
      className="relative pt-10 pb-12 sm:pt-16 sm:pb-16 md:pt-24 md:pb-20 px-4 sm:px-6 max-w-7xl mx-auto text-center flex flex-col items-center"
    >
      {/* Decorative background glow */}
      <div
        className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-[#2DD4BF]/10 rounded-full blur-3xl pointer-events-none -z-10"
        aria-hidden="true"
      />

      {/* Eyebrow */}
      <div className="anime-reveal inline-flex items-center gap-2 px-3 py-1 rounded-sm bg-[#111C2E] border border-white/5 text-[11px] font-mono tracking-widest text-[#2DD4BF] uppercase mb-6">
        <span>UNOFFICIAL CAMPUS GATEWAY</span>
      </div>

      {/* H1 Heading */}
      <h1 className="anime-reveal font-display text-3xl sm:text-5xl md:text-6xl font-bold tracking-tight text-[#E6EDF3] max-w-4xl leading-[1.1] mb-6">
        Satu Antarmuka REST API untuk Seluruh Layanan Kampus UBSI.
      </h1>

      {/* Subtitle */}
      <p className="anime-reveal text-[#94A7BC] text-base sm:text-lg md:text-xl max-w-2xl leading-relaxed mb-10 font-sans">
        Agregator data modern berkecepatan tinggi untuk SIAKAD, MyBest Elearning, E-Library,
        Repository, dan E-Journal dengan format JSON terstandarisasi dan Redis cache sub-250ms.
      </p>

      {/* CTA Buttons */}
      <div className="anime-reveal flex flex-wrap items-center justify-center gap-4 w-full sm:w-auto">
        <a
          href="#showcase"
          className="w-full sm:w-auto inline-flex items-center justify-center px-6 py-3.5 rounded-md bg-[#2DD4BF] hover:bg-[#54E3D1] text-[#06251F] font-semibold text-sm transition-colors shadow-float"
        >
          Lihat Contoh Response
        </a>
        <a
          href="https://github.com/MuaraAI/UBSI-API"
          target="_blank"
          rel="noopener noreferrer"
          className="w-full sm:w-auto inline-flex items-center justify-center px-6 py-3.5 rounded-md bg-[#111C2E] hover:bg-[#17263D] text-[#E6EDF3] font-semibold text-sm border border-white/10 hover:border-[#2DD4BF]/50 transition-colors"
        >
          GitHub Repository
        </a>
      </div>

      {/* Trust & Architecture Pills */}
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
