import { NextResponse } from "next/server";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

// Proxy sisi-server untuk Rekap Nilai: browser tidak perlu tahu API key.
// Urutan konfigurasi: env UBSI_API_KEY/UBSI_BACKEND_URL -> .env root repo -> default lokal.

export const dynamic = "force-dynamic";

const DEFAULT_BACKEND = "http://127.0.0.1:8300";

function parseRootEnv(): Record<string, string> {
  // web/ berada satu level di bawah root repo; .env backend ada di root.
  try {
    const content = readFileSync(resolve(process.cwd(), "..", ".env"), "utf-8");
    const vars: Record<string, string> = {};
    for (const line of content.split(/\r?\n/)) {
      const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*?)\s*$/);
      if (m) vars[m[1]] = m[2];
    }
    return vars;
  } catch {
    return {};
  }
}

function resolveConfig() {
  const rootEnv = parseRootEnv();
  const backendUrl = (
    process.env.UBSI_BACKEND_URL ||
    (rootEnv.HOST && rootEnv.PORT
      ? `http://${rootEnv.HOST}:${rootEnv.PORT}`
      : DEFAULT_BACKEND)
  ).replace(/\/+$/, "");
  const apiKey = process.env.UBSI_API_KEY || rootEnv.API_KEY || "";
  return { backendUrl, apiKey };
}

export async function GET() {
  const { backendUrl, apiKey } = resolveConfig();

  if (!apiKey) {
    return NextResponse.json(
      {
        success: false,
        backend: backendUrl,
        error: {
          code: "NO_API_KEY",
          message: "API key belum tersedia di sisi server",
          hint: "Set API_KEY di berkas .env root repo, lalu restart server web.",
        },
      },
      { status: 500 }
    );
  }

  try {
    const res = await fetch(`${backendUrl}/v1/elearning/grades`, {
      headers: { "X-API-Key": apiKey, Accept: "application/json" },
      signal: AbortSignal.timeout(90_000),
      cache: "no-store",
    });

    let body: {
      success?: boolean;
      data?: unknown;
      cached?: boolean;
      stale?: boolean;
      error?: { code?: string; message?: string };
    } | null = null;
    try {
      body = await res.json();
    } catch {
      body = null;
    }

    if (!res.ok || !body?.success) {
      const code = body?.error?.code ?? `HTTP_${res.status}`;
      const hints: Record<string, string> = {
        CONFIG_MISSING:
          "Set ELEARNING_NIM dan ELEARNING_PASS di berkas .env backend, lalu restart server backend.",
        AUTH_FAILED:
          "Periksa ELEARNING_NIM / ELEARNING_PASS di .env backend, atau coba lagi — captcha kampus kadang gagal pada percobaan pertama.",
        HTTP_401:
          "Nilai API_KEY di .env backend berbeda dengan yang dipakai server web.",
        HTTP_429:
          "Batas 60 request/menit terlampaui. Tunggu sebentar lalu muat ulang.",
      };
      return NextResponse.json(
        {
          success: false,
          backend: backendUrl,
          error: {
            code,
            message:
              body?.error?.message ??
              `Backend merespons ${res.status} tanpa detail kesalahan`,
            hint: hints[code] ?? hints[`HTTP_${res.status}`] ?? "Periksa log backend untuk detail kesalahan.",
          },
        },
        { status: res.status }
      );
    }

    return NextResponse.json({ ...body, backend: backendUrl });
  } catch {
    return NextResponse.json(
      {
        success: false,
        backend: backendUrl,
        error: {
          code: "BACKEND_UNREACHABLE",
          message: `Tidak bisa menghubungi backend di ${backendUrl}`,
          hint: "Jalankan backend di folder repo: uvicorn app.main:app --port 8300 --reload",
        },
      },
      { status: 504 }
    );
  }
}
