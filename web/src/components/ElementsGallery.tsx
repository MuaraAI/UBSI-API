import React from "react";
import styles from "./ElementsGallery.module.css";

export function ElementsGallery() {
  return (
    <section id="elements" className="py-16 px-4 sm:px-6 max-w-7xl mx-auto">
      <div className="text-center mb-10">
        <div className="badge-dark mb-4 mx-auto">
          <span className="w-2 h-2 rounded-full bg-[#92EEFF] shadow-[0_0_8px_#92EEFF] animate-pulse" />
          <span>UI ELEMENTS</span>
        </div>
        <h2 className="font-display text-2xl sm:text-3xl font-bold text-foreground mt-2">
          Elemen UI Adaptasi Uiverse.
        </h2>
        <p className="text-secondary text-sm sm:text-base mt-2 max-w-xl mx-auto font-sans">
          Elemen open-source dari Uiverse (lisensi MIT), diadaptasi ke tema glassmorphism dengan aksen ocean cyan (#92EEFF).
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
        <div className="glass-card-3d p-6 flex flex-col">
          <span className="text-xs font-mono text-[#062535] font-semibold uppercase tracking-wider mb-4">
            Button
          </span>
          <div className="flex-1 flex items-center justify-center py-8">
            <button type="button" className={styles.uwButton}>
              <span>GET STARTED</span>
            </button>
          </div>
          <p className="text-xs text-secondary leading-relaxed mt-2">
            Hover fill interaktif dari kanan ke kiri. Adaptasi dari{" "}
            <a
              href="https://uiverse.io/abrahamcalsin/sour-donkey-65"
              target="_blank"
              rel="noreferrer noopener"
              className="text-[#0369a1] hover:underline font-medium"
            >
              sour-donkey-65
            </a>
            .
          </p>
        </div>

        <div className="glass-card-3d p-6 flex flex-col">
          <span className="text-xs font-mono text-[#062535] font-semibold uppercase tracking-wider mb-4">
            Switch
          </span>
          <div className="flex-1 flex items-center justify-center py-8">
            <label className="inline-flex flex-col items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                className={styles.uwSwitchInput}
                aria-label="Toggle scraper"
              />
              <span className={styles.uwSwitch}>
                <svg
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                  aria-hidden="true"
                >
                  <path d="M12 2C8.13 2 5 5.13 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26c1.81-1.27 3-3.36 3-5.74 0-3.87-3.13-7-7-7zm0 2c2.76 0 5 2.24 5 5 0 1.98-1.16 3.7-2.83 4.51-.4.19-.67.59-.67 1.04V16h-3v-1.45c0-.45-.27-.85-.67-1.04C8.16 12.7 7 10.98 7 9c0-2.76 2.24-5 5-5z" />
                  <path d="M9 20h6v1c0 .55-.45 1-1 1h-4c-.55 0-1-.45-1-1v-1z" />
                </svg>
              </span>
              <span className="text-xs font-mono text-secondary">
                Toggle scraper
              </span>
            </label>
          </div>
          <p className="text-xs text-secondary leading-relaxed mt-2">
            Glow ocean cyan (#92EEFF) saat aktif. Adaptasi dari{" "}
            <a
              href="https://uiverse.io/vinodjangid07/quick-moth-22"
              target="_blank"
              rel="noreferrer noopener"
              className="text-[#0369a1] hover:underline font-medium"
            >
              quick-moth-22
            </a>
            .
          </p>
        </div>
      </div>
    </section>
  );
}
