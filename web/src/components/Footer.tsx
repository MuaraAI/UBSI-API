import React from "react";
import { Monogram } from "./Monogram";

export function Footer() {
  return (
    <footer className="border-t border-white/5 bg-[#0D1624] py-12 px-4 sm:px-6">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
        <div>
          <div className="flex items-center gap-3">
            <Monogram className="w-8 h-8" />
            <div>
              <div className="font-display font-bold text-base text-[#E6EDF3]">
                UBSI API
              </div>
              <div className="text-xs font-mono text-[#94A7BC]">
                Muara AI: Deep Water. Local craft flows global.
              </div>
            </div>
          </div>
        </div>

        <p className="text-[11px] font-mono text-[#94A7BC] text-center md:text-right max-w-md leading-relaxed">
          UBSI API adalah proyek riset independen non-komersial komunitas Muara AI dan tidak berafiliasi secara resmi dengan institusi Universitas Bina Sarana Informatika.
        </p>

        <div className="flex items-center gap-4 text-xs font-mono text-[#94A7BC]">
          <span>MIT License</span>
          <span>•</span>
          <a
            href="https://github.com/MuaraAI/UBSI-API/releases"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-[#2DD4BF] transition-colors"
          >
            v1.1.0 Stable
          </a>
        </div>
      </div>
    </footer>
  );
}
