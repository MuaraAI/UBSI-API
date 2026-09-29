import React from "react";

export function Quickstart() {
  return (
    <section id="quickstart" className="py-16 px-4 sm:px-6 max-w-7xl mx-auto">
      <div className="text-center mb-10">
        <span className="accent-badge text-xs font-mono tracking-widest uppercase">
          INSTALLATION IN 3 MINUTES
        </span>
        <h2 className="font-display text-2xl sm:text-3xl font-bold text-foreground mt-3">
          Jalankan Local Server UBSI API.
        </h2>
        <p className="text-secondary text-sm sm:text-base mt-2 max-w-xl mx-auto font-sans">
          Ikuti panduan mudah 3 langkah untuk menjalankan backend aggregator di mesin Anda sendiri.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="glass-card p-7 flex flex-col justify-between">
          <div>
            <span className="w-9 h-9 rounded-full bg-accent/10 border border-accent/30 text-accent font-mono text-sm font-bold flex items-center justify-center mb-4">
              1
            </span>
            <h3 className="font-display text-base font-semibold text-foreground">
              Clone & Setup Environment
            </h3>
            <p className="text-xs text-secondary mt-2 mb-4 leading-relaxed font-sans">
              Unduh repositori resmi dan aktifkan virtual environment Python 3.10+.
            </p>
          </div>
          <pre className="p-3 rounded-sm bg-code-bg font-mono text-xs text-code-text overflow-x-auto border border-white/10 leading-relaxed">
            <code>{`git clone https://github.com/MuaraAI/UBSI-API.git
cd UBSI-API && python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt`}</code>
          </pre>
        </div>

        <div className="glass-card p-7 flex flex-col justify-between">
          <div>
            <span className="w-9 h-9 rounded-full bg-accent/10 border border-accent/30 text-accent font-mono text-sm font-bold flex items-center justify-center mb-4">
              2
            </span>
            <h3 className="font-display text-base font-semibold text-foreground">
              Konfigurasi Berkas .env
            </h3>
            <p className="text-xs text-secondary mt-2 mb-4 leading-relaxed font-sans">
              Salin contoh konfigurasi dan masukkan API Key serta kredensial akun SIAKAD.
            </p>
          </div>
          <pre className="p-3 rounded-sm bg-code-bg font-mono text-xs text-code-text overflow-x-auto border border-white/10 leading-relaxed">
            <code>{`cp .env.example .env
# Edit .env:
# API_KEY=kunci_rahasia_anda
# STUDENTV2_NIM=15260767
# STUDENTV2_PASS=password_anda`}</code>
          </pre>
        </div>

        <div className="glass-card p-7 flex flex-col justify-between">
          <div>
            <span className="w-9 h-9 rounded-full bg-accent/10 border border-accent/30 text-accent font-mono text-sm font-bold flex items-center justify-center mb-4">
              3
            </span>
            <h3 className="font-display text-base font-semibold text-foreground">
              Jalankan Server Uvicorn
            </h3>
            <p className="text-xs text-secondary mt-2 mb-4 leading-relaxed font-sans">
              Backend otomatis aktif pada port 8300 dengan dokumentasi Swagger interaktif.
            </p>
          </div>
          <pre className="p-3 rounded-sm bg-code-bg font-mono text-xs text-code-text overflow-x-auto border border-white/10 leading-relaxed">
            <code>{`uvicorn app.main:app --port 8300 --reload
# Buka Swagger UI:
# http://127.0.0.1:8300/docs`}</code>
          </pre>
        </div>
      </div>
    </section>
  );
}
