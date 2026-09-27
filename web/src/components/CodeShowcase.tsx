"use client";

import React, { useState } from "react";
import { CODE_EXAMPLES } from "@/data/codeExamples";

export function CodeShowcase() {
  const [activeTab, setActiveTab] = useState<"curl" | "python" | "typescript">("curl");
  const [copied, setCopied] = useState(false);

  const activeExample = CODE_EXAMPLES[activeTab];

  const handleCopy = async () => {
    try {
      if (typeof navigator !== "undefined" && navigator.clipboard) {
        await navigator.clipboard.writeText(activeExample.snippet);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }
    } catch {
      // Fallback silent handling
    }
  };

  return (
    <section id="showcase" className="py-16 px-4 sm:px-6 max-w-7xl mx-auto">
      <div className="text-center mb-10">
        <span className="text-xs font-mono text-[#2DD4BF] tracking-widest uppercase">
          DEVELOPER EXPERIENCE
        </span>
        <h2 className="font-display text-2xl sm:text-3xl font-bold text-[#E6EDF3] mt-2">
          Interaksi Cepat, Response Terstandarisasi.
        </h2>
        <p className="text-[#94A7BC] text-sm sm:text-base mt-2 max-w-xl mx-auto font-sans">
          Panggil data mata kuliah aktif MyBest Elearning secara langsung dengan header autentikasi terisolasi.
        </p>
      </div>

      <div className="rounded-lg bg-[#111C2E] border border-white/10 shadow-float overflow-hidden">
        <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-3 bg-[#0D1624] border-b border-white/5">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-[#F87171]/80 inline-block" />
            <span className="w-3 h-3 rounded-full bg-[#FBBF24]/80 inline-block" />
            <span className="w-3 h-3 rounded-full bg-[#34D399]/80 inline-block" />
            <span className="text-xs font-mono text-[#94A7BC] ml-2 hidden sm:inline">
              GET /v1/elearning/courses
            </span>
          </div>

          <div className="flex items-center gap-2 ml-auto sm:ml-0">
            <div className="flex items-center gap-1 bg-[#0A1220] p-1 rounded-md border border-white/5">
              {(["curl", "python", "typescript"] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-2.5 py-1 rounded text-xs font-mono transition-colors ${
                    activeTab === tab
                      ? "bg-[#111C2E] text-[#2DD4BF] font-semibold"
                      : "text-[#94A7BC] hover:text-[#E6EDF3]"
                  }`}
                >
                  {tab === "curl" ? "cURL" : tab === "python" ? "Python" : "TypeScript"}
                </button>
              ))}
            </div>

            <button
              onClick={handleCopy}
              className="inline-flex items-center gap-1.5 px-3 py-1 rounded bg-[#17263D] hover:bg-[#1C2F4C] text-xs font-mono text-[#E6EDF3] transition-colors border border-white/5 shrink-0"
              aria-label="Salin snippet kode"
            >
              <span>{copied ? "Disalin!" : "Salin"}</span>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 divide-y lg:divide-y-0 lg:divide-x divide-white/5">
          <div className="p-4 sm:p-6 bg-[#0A1220]/60 overflow-x-auto">
            <div className="flex items-center justify-between text-xs font-mono text-[#94A7BC] mb-3">
              <span>REQUEST SNIPPET</span>
              <span className="text-[#2DD4BF]">X-API-Key: ••••••••</span>
            </div>
            <pre className="font-mono text-xs sm:text-sm text-[#E6EDF3] leading-relaxed whitespace-pre">
              <code>{activeExample.snippet}</code>
            </pre>
          </div>

          <div className="p-4 sm:p-6 bg-[#111C2E] overflow-x-auto">
            <div className="flex items-center justify-between text-xs font-mono text-[#94A7BC] mb-3">
              <span>RESPONSE PAYLOAD (JSON)</span>
              <div className="flex items-center gap-2">
                <span className="text-emerald-400 font-semibold">200 OK</span>
                <span className="text-[#94A7BC]">• {activeExample.latencyMs}ms</span>
              </div>
            </div>
            <pre className="font-mono text-xs text-[#94A7BC] leading-relaxed whitespace-pre max-h-[360px] overflow-y-auto">
              <code>{activeExample.response}</code>
            </pre>
          </div>
        </div>
      </div>
    </section>
  );
}
