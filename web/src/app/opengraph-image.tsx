import { ImageResponse } from "next/og";

export const runtime = "edge";

export const alt = "UBSI API: Unofficial REST API Aggregator 6 Layanan Kampus UBSI";
export const size = {
  width: 1200,
  height: 630,
};
export const contentType = "image/png";

export default async function Image() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "flex-start",
          justifyContent: "space-between",
          backgroundColor: "#0A1220",
          padding: "64px 80px",
          fontFamily: "sans-serif",
          border: "8px solid #111C2E",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          <div
            style={{
              width: "48px",
              height: "48px",
              backgroundColor: "#111C2E",
              borderRadius: "10px",
              border: "2px solid #92EEFF",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#92EEFF",
              fontSize: "24px",
              fontWeight: "bold",
            }}
          >
            M
          </div>
          <div style={{ display: "flex", flexDirection: "column" }}>
            <span style={{ color: "#E6EDF3", fontSize: "28px", fontWeight: "bold" }}>
              UBSI API
            </span>
            <span style={{ color: "#92EEFF", fontSize: "14px", letterSpacing: "2px" }}>
              MUARA AI • DEEP WATER
            </span>
          </div>
        </div>

        <div style={{ display: "flex", flexDirection: "column", maxWidth: "950px" }}>
          <span
            style={{
              color: "#E6EDF3",
              fontSize: "50px",
              fontWeight: 800,
              lineHeight: 1.15,
              marginBottom: "16px",
            }}
          >
            Satu Antarmuka REST API untuk Seluruh Layanan Kampus UBSI.
          </span>
          <span style={{ color: "#94A7BC", fontSize: "24px", lineHeight: 1.4 }}>
            SIAKAD • MyBest Elearning • E-Journal (23 Jurnal) • E-Library • Repository • News
          </span>
        </div>

        <div style={{ display: "flex", gap: "20px" }}>
          <div
            style={{
              backgroundColor: "#111C2E",
              padding: "10px 20px",
              borderRadius: "8px",
              color: "#92EEFF",
              fontSize: "18px",
              border: "1px solid rgba(255,255,255,0.1)",
            }}
          >
            Sub-250ms Redis Cache
          </div>
          <div
            style={{
              backgroundColor: "#111C2E",
              padding: "10px 20px",
              borderRadius: "8px",
              color: "#92EEFF",
              fontSize: "18px",
              border: "1px solid rgba(255,255,255,0.1)",
            }}
          >
            Open Source • MIT
          </div>
          <div
            style={{
              backgroundColor: "#111C2E",
              padding: "10px 20px",
              borderRadius: "8px",
              color: "#E6EDF3",
              fontSize: "18px",
              border: "1px solid rgba(255,255,255,0.1)",
            }}
          >
            v1.1.0 Stable
          </div>
        </div>
      </div>
    ),
    {
      ...size,
    }
  );
}
